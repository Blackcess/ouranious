"""Shared SQL candidate filtering for the six identity repositories."""

from collections.abc import Iterable
from uuid import UUID

from pymysql.connections import Connection

from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityReference,
    LifecycleState,
)
from repositories.utils.candidate_page import CandidatePage
from utils.identity_names import normalize_identity_name


def find_identity_candidate_ids(
    *,
    kind: IdentityKind,
    canonical_name: str,
    aliases: Iterable[str],
    exclude_reference: UUID | IdentityReference | None,
    include_retired: bool,
    limit: int,
    connection: Connection,
) -> CandidatePage[bytes]:
    """Find bounded identity IDs whose canonical name or alias matches.

    The first query uses the existing name and alias indexes. The second query
    handles the approved trim/collapse-whitespace/casefold normalization without
    returning the underlying identity table to Python. Its functional predicates
    may scan rows of this kind; a persisted normalized search key would be needed
    to make that fallback index-backed.
    """

    if not isinstance(kind, IdentityKind):
        raise TypeError("kind must be an IdentityKind")
    if not isinstance(canonical_name, str):
        raise TypeError("canonical_name must be a string")
    alias_values = tuple(aliases)
    if any(not isinstance(alias, str) for alias in alias_values):
        raise TypeError("aliases must contain only strings")
    if not isinstance(include_retired, bool):
        raise TypeError("include_retired must be a boolean")
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    input_names = tuple(
        dict.fromkeys(
            name for name in (canonical_name, *alias_values) if name.strip()
        )
    )
    if not input_names:
        return CandidatePage(())
    normalized_names = tuple(
        dict.fromkeys(normalize_identity_name(name) for name in input_names)
    )
    if not normalized_names:
        return CandidatePage(())

    exclude_id = _reference_bytes(exclude_reference)
    filter_sql = "i.kind = %s"
    filter_params: list[object] = [kind.value]
    if not include_retired:
        filter_sql += " AND i.lifecycle_state = %s"
        filter_params.append(LifecycleState.CANONICAL.value)
    if exclude_id is not None:
        filter_sql += " AND i.identity_id <> %s"
        filter_params.append(exclude_id)

    exact_name_marks = ", ".join(["%s"] * len(input_names))
    normalized_name_marks = ", ".join(["%s"] * len(normalized_names))
    exact_query = f"""
        SELECT i.identity_id
        FROM identities AS i
        WHERE {filter_sql}
          AND (
            i.canonical_name IN ({exact_name_marks})
            OR EXISTS (
                SELECT 1
                FROM identity_aliases AS a
                WHERE a.identity_id = i.identity_id
                  AND a.alias IN ({exact_name_marks})
            )
          )
        ORDER BY i.identity_id
        LIMIT %s
    """
    normalized_query = f"""
        SELECT i.identity_id
        FROM identities AS i
        WHERE {filter_sql}
          AND (
            LOWER(TRIM(REGEXP_REPLACE(i.canonical_name, '[[:space:]]+', ' ')))
                COLLATE utf8mb4_0900_as_cs IN ({normalized_name_marks})
            OR EXISTS (
                SELECT 1
                FROM identity_aliases AS a
                WHERE a.identity_id = i.identity_id
                  AND LOWER(TRIM(REGEXP_REPLACE(a.alias, '[[:space:]]+', ' ')))
                      COLLATE utf8mb4_0900_as_cs IN ({normalized_name_marks})
            )
          )
        ORDER BY i.identity_id
        LIMIT %s
    """
    query_limit = limit + 1

    with connection.cursor() as cursor:
        cursor.execute(
            exact_query,
            (*filter_params, *input_names, *input_names, query_limit),
        )
        exact_rows = cursor.fetchall()

        cursor.execute(
            normalized_query,
            (*filter_params, *normalized_names, *normalized_names, query_limit),
        )
        normalized_rows = cursor.fetchall()

    exact_ids = [row["identity_id"] for row in exact_rows]
    normalized_ids = [row["identity_id"] for row in normalized_rows]
    all_ids = sorted(set(exact_ids) | set(normalized_ids))
    truncated = (
        len(exact_ids) > limit
        or len(normalized_ids) > limit
        or len(all_ids) > limit
    )

    return CandidatePage(tuple(all_ids[:limit]), truncated)


def _reference_bytes(reference: UUID | IdentityReference | None) -> bytes | None:
    if reference is None:
        return None
    if isinstance(reference, IdentityReference):
        return reference.value.bytes
    if isinstance(reference, UUID):
        return reference.bytes
    raise TypeError("exclude_reference must be UUID, IdentityReference, or None")
