from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from enum import StrEnum


class AvailabilityStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ProductAvailabilityProperties:
    launch_date: date | None = None
    discontinuation_date: date | None = None
    availability_status: AvailabilityStatus | None = None

    def __post_init__(self):
        if self.launch_date is not None and self.discontinuation_date is not None:
            if self.launch_date > self.discontinuation_date:
                raise ValueError("Launch date cannot be after discontinuation date.")

        # validate date type
        if self.launch_date is not None and not isinstance(self.launch_date, date):
            raise TypeError("Launch date must be a date object.")

        if self.discontinuation_date is not None and not isinstance(self.discontinuation_date, date):
            raise TypeError("Discontinuation date must be a date object.")
        