from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from enum import Enum
import re
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import InvestmentStage


@dataclass(frozen=True)
class InvestmentProperties:
    investment_amount: Decimal | None = None
    currency: str | None = None
    investment_date: date | None = None
    funding_round: InvestmentStage | None = None
    pre_money_valuation: Decimal | None = None
    post_money_valuation: Decimal | None = None
    equity_percentage: Decimal | None = None
    is_lead_investor: bool | None = None

    def __post_init__(self):

        # 1. Validate investment date
        if self.investment_date is not None:

            if isinstance(self.investment_date, datetime):
                raise TypeError(
                    "Investment date must be a date object, "
                    "not a datetime object."
                )

            if not isinstance(self.investment_date, date):
                raise TypeError(
                    "Investment date must be a datetime.date object."
                )

            if self.investment_date > date.today():
                raise ValueError(
                    "Investment date cannot be in the future."
                )

        # 2. Validate currency
        if self.currency is not None:

            if not isinstance(self.currency, str):
                raise TypeError("Currency must be a string.")

            if not re.fullmatch(r"[A-Z]{3}", self.currency):
                raise ValueError(
                    "Currency must be a three-letter uppercase "
                    "ISO 4217 currency code."
                )

        # 3. Validate monetary values
        monetary_fields = (
            "investment_amount",
            "pre_money_valuation",
            "post_money_valuation",
        )

        for field_name in monetary_fields:
            value = getattr(self, field_name)

            if value is not None:

                if not isinstance(value, Decimal):
                    raise TypeError(
                        f"{field_name} must be a Decimal object."
                    )

                if not value.is_finite():
                    raise ValueError(
                        f"{field_name} must be a finite Decimal."
                    )

                if value < Decimal("0"):
                    raise ValueError(
                        f"{field_name} cannot be negative."
                    )

        # 4. Validate equity percentage
        if self.equity_percentage is not None:

            if not isinstance(self.equity_percentage, Decimal):
                raise TypeError(
                    "Equity percentage must be a Decimal object."
                )

            if not self.equity_percentage.is_finite():
                raise ValueError(
                    "Equity percentage must be finite."
                )

            if not Decimal("0") <= self.equity_percentage <= Decimal("100"):
                raise ValueError(
                    "Equity percentage must be between 0 and 100."
                )

        # 5. Validate funding round
        if self.funding_round is not None:
            if not isinstance(self.funding_round, InvestmentStage):
                raise TypeError(
                    "Funding round must be an InvestmentStage enum."
                )

        # 6. Validate lead investor flag
        if self.is_lead_investor is not None:
            if not isinstance(self.is_lead_investor, bool):
                raise TypeError(
                    "is_lead_investor must be a boolean."
                )

        # ensure that if any monetary value is provided, currency must also be provided
        monetary_values = [
            self.investment_amount,
            self.pre_money_valuation,
            self.post_money_valuation,
        ]
        if any(value is not None for value in monetary_values) and self.currency is None:
            raise ValueError(
                "Currency must be provided if any monetary value is specified."
            )


        