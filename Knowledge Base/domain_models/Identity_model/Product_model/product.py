from domain_models.Identity_model.identity import Identity, IdentityKind, IdentityRepresentations, IdentityReference, LifecycleState

class Product(Identity):

    def __init__(
        self,
        *,
        representations: IdentityRepresentations,
        reference: IdentityReference | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL
    ):
        super().__init__(
            kind = IdentityKind.PRODUCT,
            representations= representations,
            reference= reference,
            lifecycle_state= lifecycle_state
        )
    