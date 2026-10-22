from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from enum import StrEnum

class AcquisitionType(StrEnum):
    FULL_ACQUISITION = "full_acquisition"
    PARTIAL_ACQUISITION = "partial_acquisition"
    MAJORITY_ACQUISITION = "majority_acquisition"
    MINORITY_ACQUISITION = "minority_acquisition"
    MERGER = "merger"
    ASSET_ACQUISITION = "asset_acquisition"
    ACQUIHIRE = "acquihire"
    MANAGEMENT_BUYOUT = "management_buyout"
    LEVERAGED_BUYOUT = "leveraged_buyout"
    REVERSE_ACQUISITION = "reverse_acquisition"
    OTHER = "other"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class AcquisitionProperties:
    acquisition_date: date | None = None
    acquisition_amount: Decimal | None = None
    currency: str | None = None
    ownership_percentage_acquired: Decimal | None = None
    acquisition_type: AcquisitionType | None = None

    def __post_init__(self):
        # Validate acquisition amount
        if self.acquisition_amount is not None:
            if not isinstance(self.acquisition_amount, Decimal):
                raise TypeError("Acquisition amount must be a Decimal object.")
            if not self.acquisition_amount.is_finite():
                raise ValueError("Acquisition amount must be a finite number.")
            if self.acquisition_amount < Decimal("0"):
                raise ValueError("Acquisition amount cannot be negative.")

        # Validate ownership percentage acquired
        if self.ownership_percentage_acquired is not None:
            if not isinstance(self.ownership_percentage_acquired, Decimal):
                raise TypeError(
                    "Ownership percentage acquired must be a Decimal object."
                )
            if not self.ownership_percentage_acquired.is_finite():
                raise ValueError(
                    "Ownership percentage acquired must be a finite number."
                )
            if not Decimal("0") <= self.ownership_percentage_acquired <= Decimal("100"):
                raise ValueError(
                    "Ownership percentage acquired must be between 0 and 100."
                )

        # Validate acquisition type
        if self.acquisition_type is not None:
            if not isinstance(self.acquisition_type, AcquisitionType):
                raise TypeError(
                    "Acquisition type must be an AcquisitionType enum."
                )

        # validate acquisition date
        if self.acquisition_date is not None:
            if not isinstance(self.acquisition_date, date):
                raise TypeError("Acquisition date must be a datetime.date object.")
            
        # ensure that if acquisition amount is provided, currency must also be provided
        if self.acquisition_amount is not None and self.currency is None:
            raise ValueError(
                "Currency must be provided if acquisition amount is specified."
            )