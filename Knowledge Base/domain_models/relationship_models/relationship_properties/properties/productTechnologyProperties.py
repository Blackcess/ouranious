from dataclasses import dataclass
from decimal import Decimal
from datetime import date

@dataclass(frozen=True)
class ProductTechnologyProperties:
    adoption_date: date | None = None
    is_core_technology: bool | None = None

    def __post_init__(self):
        if self.adoption_date is not None and not isinstance(self.adoption_date, date):
            raise ValueError("adoption_date must be a date object or None")
        if self.is_core_technology is not None and not isinstance(self.is_core_technology, bool):
            raise ValueError("is_core_technology must be a boolean or None")