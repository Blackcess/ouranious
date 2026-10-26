from datetime import timezone
from uuid import UUID

from pymysql.connections import Connection
from pymysql.err import IntegrityError

from domain_models.Provenance.source import Source, SourceReference, SourceType
from repositories.utils.errors import RepositoryIntegrityError, translate_integrity_error


def _source_uuid_bytes(reference: UUID | SourceReference) -> bytes:
    if isinstance(reference, SourceReference):
        return reference.value.bytes
    if isinstance(reference, UUID):
        return reference.bytes
    raise TypeError("reference must be a UUID or SourceReference")


class SourceRepository:
    """Persist and reconstruct independent source metadata records."""

    def create(self, source: Source, *, connection: Connection) -> None:
        if not isinstance(source, Source):
            raise TypeError("source must be a Source")
        retrieved_at = source.retrieved_at.astimezone(timezone.utc).replace(tzinfo=None)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO sources
                       (source_id, title, source_type, publisher, url, publication_date, retrieved_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        source.reference.value.bytes,
                        source.title,
                        source.source_type.value,
                        source.publisher,
                        source.url,
                        source.publication_date,
                        retrieved_at,
                    ),
                )
        except IntegrityError as exc:
            raise translate_integrity_error("Creating source", exc) from exc

    def get_by_reference(
        self, reference: UUID | SourceReference, *, connection: Connection
    ) -> Source | None:
        source_id = _source_uuid_bytes(reference)
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT source_id, title, source_type, publisher, url,
                          publication_date, retrieved_at
                   FROM sources WHERE source_id = %s""",
                (source_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        try:
            retrieved_at = row["retrieved_at"]
            if retrieved_at.tzinfo is None:
                retrieved_at = retrieved_at.replace(tzinfo=timezone.utc)
            else:
                retrieved_at = retrieved_at.astimezone(timezone.utc)
            return Source(
                title=row["title"],
                source_type=SourceType(row["source_type"]),
                reference=SourceReference(UUID(bytes=row["source_id"])),
                publisher=row["publisher"],
                url=row["url"],
                publication_date=row["publication_date"],
                retrieved_at=retrieved_at,
            )
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise RepositoryIntegrityError("Invalid persisted source record.") from exc

    def exists(self, reference: UUID | SourceReference, *, connection: Connection) -> bool:
        source_id = _source_uuid_bytes(reference)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM sources WHERE source_id = %s", (source_id,))
            return cursor.fetchone() is not None
