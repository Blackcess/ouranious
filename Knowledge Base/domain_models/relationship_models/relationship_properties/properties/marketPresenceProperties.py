from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from enum import StrEnum


class OperatingStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass(frozen=True)
class MarketPresenceProperties:
    entry_date: date | None = None
    exit_date: date | None = None
    is_current: bool | None = None
    operating_status: OperatingStatus | None = None

    def __post_init__(self):
        if self.is_current is not None and self.operating_status is not None:
            if self.is_current and self.operating_status != OperatingStatus.ACTIVE:
                raise ValueError("If is_current is True, operating_status must be 'Active'.")
            elif not self.is_current and self.operating_status == OperatingStatus.ACTIVE:
                raise ValueError("If is_current is False, operating_status cannot be 'Active'.")

        # validate that entry_date is before exit_date if both are provided
        if self.entry_date is not None and self.exit_date is not None:
            if self.entry_date >= self.exit_date:
                raise ValueError("entry_date must be before exit_date.")