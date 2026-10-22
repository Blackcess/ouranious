from domain_models.Identity_model.Organisation_model.organisation import Organisation
from domain_models.Identity_model.Organisation_model.organisation_classification import OrganisationClassification
from domain_models.Identity_model.identity import IdentityRepresentations, IdentityReference, LifecycleState
from domain_models.Identity_model.Person_model.person import Person
from domain_models.Identity_model.Place_model.place import Place, PlaceKind
from domain_models.Identity_model.Industry_model.industry import Industry
from domain_models.Identity_model.Product_model.product import Product
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import Investor, InvestmentStage, InvestmentTypes
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import Startup, StartupStages, StartupBusinessModels

from domain_models.relationship_models.knowledge_graph.knowledge_graph import Knowledge_Graph
from domain_models.relationship_models.relationship import Relationship
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType

# 1. MoneyPoint

# 1.1 create an instance of Organisation for MoneyPoint
moneypoint = Organisation(
    representations= IdentityRepresentations(
        canonical_name = "MoneyPoint",
        aliases = {
            "MoneyPoint", 
            "Money Point",
            "MoneyPoint Inc",
            "Moniepoint",
            "TeamApt",
            "TeamApt Inc"
            }
    ),
    classifications={OrganisationClassification.STARTUP}
)

# 1.11 add classifications to the organisation
moneypoint.add_classification_model(OrganisationClassification.STARTUP, Startup(
    founding_year=2015,
    stage=StartupStages.SERIES_C,
    business_model=StartupBusinessModels.B2C
))

# 1.2 create instance(s) of founders for MoneyPoint

tosin = Person(
    representations=IdentityRepresentations(
        canonical_name="Tosin Eniolorunda",
        aliases = {
            "Tosin", "Tosin E", "Tosin Eni", "Tosin Eniolorunda"
        }
    )
)

felix = Person(
    representations=IdentityRepresentations(
        canonical_name="Felix Ike",
        aliases = {
            "Felix", "Felix I", "Felix Ike"
        }
    )
)

# 3. create instances of moneypoint geographical locations

lagos = Place(
    representations=IdentityRepresentations(
        canonical_name="Lagos",
        aliases = {
            "Lagos", "Lagos State", "Lagos, Nigeria"
        }
    ),
    place_kind=PlaceKind.CITY
)

nigeria = Place(
    representations=IdentityRepresentations(
        canonical_name="Nigeria",
        aliases = {
            "Nigeria", "Federal Republic of Nigeria"
        }
    ),
    place_kind=PlaceKind.COUNTRY
)

# 4. create moneypoint industry instance

fintech = Industry(
    representations=IdentityRepresentations(
        canonical_name="Fintech",
        aliases = {
            "Fintech", "Financial Technology"
        }
    )
)

# 5. create moneypoint products and services instances

monie_world = Product(
    representations=IdentityRepresentations(
        canonical_name="MonieWorld",
        aliases = {
            "MonieWorld", "Monie World"
        }
    )
)

# 6. Investors
development_partners_international = Organisation(
    representations= IdentityRepresentations(
        canonical_name="Development Partners International",
        aliases={}
    ),
    classifications={OrganisationClassification.INVESTOR}
)
leap_frog_investments = Organisation(
    representations= IdentityRepresentations(
        canonical_name="Leap Frog Investments",
        aliases={}
    ),
    classifications={OrganisationClassification.INVESTOR}
)
light_rock = Organisation(
    representations= IdentityRepresentations(
        canonical_name="Lightrock",
        aliases={"Light Rock"}
    ),
    classifications={OrganisationClassification.INVESTOR}
)
alder_tree_investments = Organisation(
    representations= IdentityRepresentations(
        canonical_name="Alder Tree Investments",
        aliases={""}
    ),
    classifications={OrganisationClassification.INVESTOR}
)
orda_africa = Organisation(
    representations=IdentityRepresentations(
        canonical_name="Orda Africa",
        aliases={}
    ),
    classifications={OrganisationClassification.STARTUP}
) 

development_partners_international.add_classification_model(OrganisationClassification.INVESTOR, Investor(investor_type=InvestmentTypes.PRIVATE_EQUITY, investment_stage=InvestmentStage.SERIES_C))
leap_frog_investments.add_classification_model(OrganisationClassification.INVESTOR, Investor(investor_type=InvestmentTypes.PRIVATE_EQUITY, investment_stage=InvestmentStage.SERIES_C))
light_rock.add_classification_model(OrganisationClassification.INVESTOR, Investor(investor_type=InvestmentTypes.PRIVATE_EQUITY, investment_stage=InvestmentStage.SERIES_C))
alder_tree_investments.add_classification_model(OrganisationClassification.INVESTOR, Investor(investor_type=InvestmentTypes.PRIVATE_EQUITY, investment_stage=InvestmentStage.SERIES_C))
orda_africa.add_classification_model(OrganisationClassification.STARTUP, Startup(founding_year=2023, stage=StartupStages.SEED, business_model= StartupBusinessModels.B2B))




# Knowledge Graph
knowledge_graph = Knowledge_Graph()
identities = [
    moneypoint,
    tosin,
    felix,
    lagos,
    nigeria, 
    fintech, 
    monie_world,
    development_partners_international,
    leap_frog_investments,
    light_rock,
    alder_tree_investments,
    orda_africa
]

for identity in identities:
    # print(identity.reference.value)
    knowledge_graph.add_identity(identity)

knowledge_graph.add_relationship(
    Relationship(
        source=tosin,
        target=moneypoint,
        type=RelationshipType.FOUNDED
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=felix,
        target=moneypoint,
        type=RelationshipType.FOUNDED
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=moneypoint,
        target=lagos,
        type=RelationshipType.HEADQUARTERED_IN
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=lagos,
        target=nigeria,
        type=RelationshipType.LOCATED_IN
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=moneypoint,
        target=fintech,
        type=RelationshipType.OPERATES_IN_INDUSTRY
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=moneypoint,
        target=monie_world,
        type=RelationshipType.DEVELOPS
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=development_partners_international,
        target=moneypoint,
        type=RelationshipType.INVESTED_IN
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=leap_frog_investments,
        target=moneypoint,
        type=RelationshipType.INVESTED_IN
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=light_rock,
        target=moneypoint,
        type=RelationshipType.INVESTED_IN
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=alder_tree_investments,
        target=moneypoint,
        type=RelationshipType.INVESTED_IN
    )
)
knowledge_graph.add_relationship(
    Relationship(
        source=moneypoint,
        target=orda_africa,
        type=RelationshipType.ACQUIRED
    )
)


for rel in knowledge_graph.get_relationships():
    print(f"{rel.get_source().representations.canonical_name} ---{rel.get_type()}---> {rel.get_target().representations.canonical_name} \n")