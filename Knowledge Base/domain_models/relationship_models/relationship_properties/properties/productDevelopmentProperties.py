from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from enum import StrEnum

class DevelopmentStatus(StrEnum):
    IN_DEVELOPMENT = "indevelopment"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"

@dataclass(frozen=True)
class ProductDevelopmentProperties:
    development_start_date: date | None = None
    release_date: date | None = None
    development_status: DevelopmentStatus | None = None

    def __post_init__(self):
        if self.development_start_date is not None and self.release_date is not None and self.development_start_date > self.release_date:
            raise ValueError("development_start_date cannot be after release_date")

        # validate date is datetime.date
        if self.development_start_date is not None and not isinstance(self.development_start_date, date):
            raise TypeError("development_start_date must be a datetime.date object")

        if self.release_date is not None and not isinstance(self.release_date, date):
            raise TypeError("release_date must be a datetime.date object")