"""Database locks used to serialize resolve-and-create operations."""

from hashlib import sha256

from pymysql.connections import Connection

from domain_models.Identity_model.identity import Identity
from domain_models.relationship_models.relationship import Relationship
from utils.identity_names import normalize_identity_name


class ResolutionLockTimeout(TimeoutError):
    """Raised when a concurrent create holds a matching-key lock too long."""


def acquire_identity_resolution_locks(
    identity: Identity,
    *,
    connection: Connection,
    timeout_seconds: int = 10,
) -> None:
    """Lock each normalized name/alias until this connection closes.

    MySQL named locks are connection-scoped, so DatabaseManager's transaction
    context releases them only after commit or rollback and connection close.
    Acquiring names in sorted order prevents lock-order deadlocks.
    """

    if not isinstance(identity, Identity):
        raise TypeError("identity must be an Identity instance")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int):
        raise TypeError("timeout_seconds must be an integer")
    if timeout_seconds < 0:
        raise ValueError("timeout_seconds cannot be negative")

    normalized_names = {
        normalized
        for name in (
            identity.representations.canonical_name,
            *identity.representations.aliases,
        )
        if (normalized := normalize_identity_name(name))
    }
    lock_names = sorted(
        "okb:id:" + sha256(
            f"{identity.kind.value}\0{name}".encode("utf-8")
        ).hexdigest()[:48]
        for name in normalized_names
    )

    for lock_name in lock_names:
        with connection.cursor() as cursor:
            cursor.execute("SELECT GET_LOCK(%s, %s) AS acquired", (lock_name, timeout_seconds))
            row = cursor.fetchone()
        if row is None or row["acquired"] != 1:
            raise ResolutionLockTimeout(
                "Timed out waiting for another create operation using the same "
                "identity name or alias."
            )


def lock_relationship_endpoints(
    relationship: Relationship,
    *,
    connection: Connection,
    timeout_seconds: int = 10,
) -> None:
    """Lock existing endpoint rows in stable order for relationship creation."""

    if not isinstance(relationship, Relationship):
        raise TypeError("relationship must be a Relationship instance")
    endpoint_ids = sorted(
        {
            relationship.get_source().reference.value.bytes,
            relationship.get_target().reference.value.bytes,
        }
    )
    pair_digest = sha256(b"".join(endpoint_ids)).hexdigest()[:48]
    lock_name = f"okb:rel:{pair_digest}"
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT GET_LOCK(%s, %s) AS acquired",
            (lock_name, timeout_seconds),
        )
        lock_row = cursor.fetchone()
    if lock_row is None or lock_row["acquired"] != 1:
        raise ResolutionLockTimeout(
            "Timed out waiting for another relationship create using the same endpoints."
        )

    marks = ", ".join(["%s"] * len(endpoint_ids))
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT identity_id FROM identities "
            f"WHERE identity_id IN ({marks}) "
            "ORDER BY identity_id FOR UPDATE",
            endpoint_ids,
        )
        rows = cursor.fetchall()
    found_ids = {row["identity_id"] for row in rows}
    if found_ids != set(endpoint_ids):
        raise LookupError("Relationship endpoints must already be persisted.")
