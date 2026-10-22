from dataclasses import dataclass
from decimal import Decimal
from datetime import date

@dataclass(frozen=True)
class IndustryParticipationProperties:
    start_date: date | None = None
    end_date: date | None = None
    is_primary_industry: bool | None = None
    def __post_init__(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")