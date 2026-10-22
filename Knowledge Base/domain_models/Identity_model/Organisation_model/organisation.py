from domain_models.Identity_model.identity import Identity, IdentityKind, IdentityRepresentations, IdentityReference, LifecycleState
from domain_models.Identity_model.Organisation_model.organisation_classification import OrganisationClassification
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import Startup, StartupBusinessModels, StartupStages

class Organisation(Identity):

    def __init__(
        self,
        *,
        representations: IdentityRepresentations,
        classifications: set[OrganisationClassification],
        reference: IdentityReference | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
    ):
        super().__init__(
            kind=IdentityKind.ORGANISATION,
            representations=representations,
            reference=reference,
            lifecycle_state=lifecycle_state,
        )
        self._classifications = classifications | set()  
        self._classification_models : dict[
            OrganisationClassification,
            object
        ] = {}

    def has_classification(self, classification: OrganisationClassification) -> bool:
        return classification in self._classifications

    def add_classification(self, classification: OrganisationClassification):
        self._classifications.add(classification)

    def remove_classification(self, classification: OrganisationClassification):
        if(self.has_classification(classification)): 
            self._classifications.discard(classification)
            # remove the corresponding model if it exists
            self._classification_models.pop(classification, None)
        else:
            raise ValueError(f"Classification {classification} not found in the organisation's classifications.")
        
    def get_classifications(self) -> set[OrganisationClassification]:
        # return clone of the classifications set to prevent external modification
        return self._classifications.copy()

    def add_classification_model(self, classification:OrganisationClassification, model):
        if (not self.has_classification(classification)): 
            raise ValueError(f"Cannot add domain model without registering classification for {classification}")
        self._classification_models[classification] = model

    def get_classification_model(self, classification:OrganisationClassification):
        return self._classification_models.get(classification)



