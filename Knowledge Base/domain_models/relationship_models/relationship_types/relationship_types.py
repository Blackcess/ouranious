from enum import Enum

class RelationshipType(Enum):

    # Person → Organisation
    FOUNDED = "founded"
    LEADS = "leads"
    OWNS = "owns"

    # Person → Place
    BORN_IN = "born_in"
    LIVES_IN = "lives_in"

    # Organisation → Organisation
    PARTNERED_WITH = "partnered_with"
    INVESTED_IN = "invested_in"
    ACQUIRED = "acquired"

    # Organisation → Place
    HEADQUARTERED_IN = "headquartered_in"
    OPERATES_IN = "operates_in"

    # Organisation → Industry
    OPERATES_IN_INDUSTRY = "operates_in_industry"

    # Organisation → Product
    OFFERS = "offers"
    DEVELOPS = "develops"

    # Organisation → Technology
    USES = "uses"

    # Product → Technology
    BUILT_WITH = "built_with"

    # Product → Place
    AVAILABLE_IN = "available_in"

    # Place → Place
    LOCATED_IN = "located_in"
    PART_OF = "part_of"