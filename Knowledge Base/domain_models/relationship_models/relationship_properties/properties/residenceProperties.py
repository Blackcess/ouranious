from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime

@dataclass(frozen=True)
class ResidenceProperties:
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    residence_type: str | None = None

    def __post_init__(self):
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
                        "Residence start date cannot be later than end date."
                    )