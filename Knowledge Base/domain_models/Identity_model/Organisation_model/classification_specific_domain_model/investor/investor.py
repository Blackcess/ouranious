
from enum import Enum

class InvestmentTypes(Enum):
    VENTURE_CAPITAL = "venture_capital"
    PRIVATE_EQUITY = "private_equity"
    CORPORATE_VENTURE_CAPITAL = "corporate_venture_capital"
    ANGEL_NETWORK  = "angel_network"
    GOVERNMENT_FUND = "government_fund"



class InvestmentStage(Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B= "series_b"
    SERIES_C= "series_c"
    GROWTH = "growth"


class Investor():
    def __init__(self, investor_type, investment_stage):
        self._investor_type = investor_type
        self._investment_stage = investment_stage

    def get_investor_type(self):
        return self._investor_type

    def get_investor_stage(self):
        return self._investment_stage





# not yet modelled:
# portfolio and portfolio_companies
# founders
# sectors
# investment_geographies
# fund_sizes
# total_invested


