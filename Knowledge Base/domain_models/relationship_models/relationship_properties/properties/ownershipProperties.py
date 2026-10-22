from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from enum import StrEnum

class OwnershipType(StrEnum):
    EQUITY = "equity"
    BENEFICIAL = "beneficial"
    LEGAL = "legal"
    ECONOMIC = "economic"
    JOINT = "joint"
    OTHER = "other"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class OwnershipProperties:
    ownership_percentage: Decimal | None = None
    ownership_type: OwnershipType | None = None
    share_class: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None

    def __post_init__(self):

        # 1. Validate ownership percentage
        if self.ownership_percentage is not None:

            if not isinstance(self.ownership_percentage, Decimal):
                raise TypeError(
                    "Ownership percentage must be a Decimal object."
                )

            if not self.ownership_percentage.is_finite():
                raise ValueError(
                    "Ownership percentage must be a finite number."
                )

            if not Decimal("0") < self.ownership_percentage <= Decimal("100"):
                raise ValueError(
                    "Ownership percentage must be greater than 0 and "
                    "less than or equal to 100."
                )

        # 2. Validate ownership type
        if self.ownership_type is not None:
            if not isinstance(self.ownership_type, OwnershipType):
                raise TypeError(
                    "Ownership type must be an OwnershipType enum."
                )

        # 3. Validate dates
        for field_name, field_value in (
            ("start_date", self.start_date),
            ("end_date", self.end_date),
        ):
            if field_value is not None:

                # datetime is a subclass of date, so explicitly reject it
                if isinstance(field_value, datetime):
                    raise TypeError(
                        f"{field_name} must be a date object, "
                        "not a datetime object."
                    )

                if not isinstance(field_value, date):
                    raise TypeError(
                        f"{field_name} must be a datetime.date object."
                    )

        # 4. Validate chronological consistency
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError(
                "Ownership start date cannot be later than end date."
            )

        # 5. Validate current ownership status
        if self.is_current is not None:
            if not isinstance(self.is_current, bool):
                raise TypeError(
                    "is_current must be a boolean."
                )

        if self.is_current is True and self.end_date is not None:
            raise ValueError(
                "Current ownership cannot have an end date."
            )