from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from enum import StrEnum

class OfferingStatus(StrEnum):
    IN_DEVELOPMENT = "indevelopment"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"

@dataclass(frozen=True)
class ProductOfferingProperties:
    launch_date: date | None = None
    discontinuation_date: date | None = None
    offering_status: OfferingStatus | None = None

    def __post_init__(self):
        if self.launch_date is not None and self.discontinuation_date is not None and self.launch_date > self.discontinuation_date:
            raise ValueError("launch_date cannot be after discontinuation_date")

        # validate date is datetime.date
        if self.launch_date is not None and not isinstance(self.launch_date, date):
            raise TypeError("launch_date must be a datetime.date object")

        if self.discontinuation_date is not None and not isinstance(self.discontinuation_date, date):
            raise TypeError("discontinuation_date must be a datetime.date object")