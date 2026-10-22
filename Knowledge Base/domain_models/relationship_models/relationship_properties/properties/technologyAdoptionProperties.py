from dataclasses import dataclass
from decimal import Decimal
from datetime import date

@dataclass(frozen=True)
class TechnologyAdoptionProperties:
    adoption_date: date | None = None

    def __post_init__(self):
        # validate date is datetime.date
        if self.adoption_date is not None and not isinstance(self.adoption_date, date):
            raise TypeError("adoption_date must be a datetime.date object")