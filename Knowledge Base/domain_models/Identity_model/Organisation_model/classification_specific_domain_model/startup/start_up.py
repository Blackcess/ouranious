from enum import Enum

class StartupStages(Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D = "series_d"
    SERIES_E = "series_e"

class StartupBusinessModels(Enum):
    B2B = "b2b"
    B2C = "b2c"
    B2B2C = "b2b2c"
    C2C = "c2c"

class Startup():
    def __init__(self,founding_year: int, stage: StartupStages, business_model: StartupBusinessModels):
        self.founding_year = founding_year
        self.stage = stage
        self.business_model = business_model



        