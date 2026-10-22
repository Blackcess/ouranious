from dataclasses import dataclass
from decimal import Decimal
import re
from enum import Enum
from datetime import date


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            raise TypeError("amount must be a Decimal")

        if not self.amount.is_finite():
            raise ValueError("amount must be finite")

        if not re.fullmatch(r"[A-Z]{3}", self.currency):
            raise ValueError("currency must be a 3-letter uppercase code")





class DurationUnit(Enum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"

@dataclass(frozen=True)
class Duration:
    value: Decimal
    unit: DurationUnit
    start_date: date | None = None
    end_date: date | None = None

    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            raise TypeError("duration value must be Decimal")

        if not self.value.is_finite() or self.value <= 0:
            raise ValueError("duration value must be positive and finite")

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot precede start_date")
# add an authouritative currency registry as well 