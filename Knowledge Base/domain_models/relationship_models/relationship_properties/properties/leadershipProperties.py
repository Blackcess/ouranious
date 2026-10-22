from dataclasses import dataclass
from decimal import Decimal
from datetime import date

@dataclass(frozen=True)
class LeadershipProperties:
    position: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None

    def __post_init__(self):
        if self.start_date is not None and self.end_date is not None and self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")