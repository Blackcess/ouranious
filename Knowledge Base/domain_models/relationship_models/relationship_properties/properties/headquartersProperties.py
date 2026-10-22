from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from enum import Enum, StrEnum

class HeadquartersLevel(StrEnum):
    GLOBAL = "global"
    REGIONAL = "regional"
    NATIONAL = "national"
    LOCAL = "local"
    UNKNOWN = "unknown"

class HeadquartersFunction(StrEnum):
    REGISTERED = "registered"
    OPERATIONAL = "operational"
    ADMINISTRATIVE = "administrative"
    FINANCIAL = "financial"
    RESEARCH_AND_DEVELOPMENT = "research_and_development"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class HeadquartersProperties:
    headquarters_level: HeadquartersLevel | None = None
    headquarters_function: HeadquartersFunction | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None