from decimal import Decimal
from utils.representations import Money, Duration
from dataclasses import dataclass

@dataclass(frozen=True)
class InvestmentTerms:
    money: Money
    equity_percentage: Decimal

    def __post_init__(self):
        if not isinstance(self.money, Money):
            raise TypeError("money must be a Money object")

        if not isinstance(self.equity_percentage, Decimal):
            raise TypeError("equity_percentage must be Decimal")

        if not self.equity_percentage.is_finite():
            raise ValueError("equity_percentage must be finite")

        if not Decimal("0") <= self.equity_percentage <= Decimal("100"):
            raise ValueError("equity_percentage must be between 0 and 100")

class AcceleratorProgramme:
    def __init__(self, name, duration: Duration, investment_terms):
        self.name = name
        self.duration = duration
        self.investment_terms = investment_terms



