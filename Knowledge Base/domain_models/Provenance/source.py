
# domain_models/provenance/source.py

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class SourceType(Enum):
    OFFICIAL_WEBSITE = "official_website"
    NEWS_ARTICLE = "news_article"
    REPORT = "report"
    GOVERNMENT_RECORD = "government_record"
    ACADEMIC_PUBLICATION = "academic_publication"
    DATABASE = "database"
    SOCIAL_MEDIA = "social_media"
    OTHER = "other"


@dataclass(frozen=True)
class SourceReference:
    value: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class Source:
    title: str
    source_type: SourceType
    reference: SourceReference = field(
        default_factory=SourceReference
    )
    publisher: str | None = None
    url: str | None = None
    publication_date: date | None = None
    retrieved_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Source title cannot be empty")

        if not isinstance(self.source_type, SourceType):
            raise TypeError("source_type must be a SourceType")

        if not isinstance(self.reference, SourceReference):
            raise TypeError("reference must be a SourceReference")

        if self.publisher is not None:
            if not self.publisher.strip():
                raise ValueError(
                    "publisher must be non-empty when provided"
                )

        if self.url is not None:
            if not self.url.strip():
                raise ValueError("url must be non-empty when provided")

        if self.publication_date is not None:
            if not isinstance(self.publication_date, date):
                raise TypeError(
                    "publication_date must be a date"
                )

        if not isinstance(self.retrieved_at, datetime):
            raise TypeError("retrieved_at must be a datetime")

        if self.retrieved_at.tzinfo is None:
            raise ValueError(
                "retrieved_at must be timezone-aware"
            )
