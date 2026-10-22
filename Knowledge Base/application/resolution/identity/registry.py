"""Extensible registries for identity and organisation matching strategies."""

from collections.abc import Mapping

from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)
from domain_models.Identity_model.identity import IdentityKind

from application.resolution.identity.strategies import (
    IdentityMatchingStrategy,
    OrganisationClassificationMatchingStrategy,
)


class MissingIdentityStrategyError(LookupError):
    """Raised when an identity kind has no registered comparison strategy."""


class MissingOrganisationClassificationStrategyError(LookupError):
    """Raised when a required organisation classification has no strategy."""


class IdentityStrategyRegistry:
    """Maps every registered IdentityKind to its matching strategy."""

    def __init__(
        self,
        strategies: Mapping[IdentityKind, IdentityMatchingStrategy] | None = None,
    ):
        self._strategies: dict[IdentityKind, IdentityMatchingStrategy] = {}
        for kind, strategy in (strategies or {}).items():
            self.register(kind, strategy)

    def register(
        self,
        kind: IdentityKind,
        strategy: IdentityMatchingStrategy,
        *,
        replace: bool = False,
    ) -> None:
        if not isinstance(kind, IdentityKind):
            raise TypeError("kind must be an IdentityKind")
        if not callable(getattr(strategy, "compare", None)):
            raise TypeError("strategy must provide a callable compare method")
        if kind in self._strategies and not replace:
            raise ValueError(f"A strategy is already registered for {kind.value}")
        self._strategies[kind] = strategy

    def get(self, kind: IdentityKind) -> IdentityMatchingStrategy:
        if not isinstance(kind, IdentityKind):
            raise TypeError("kind must be an IdentityKind")
        try:
            return self._strategies[kind]
        except KeyError as exc:
            raise MissingIdentityStrategyError(
                f"No identity matching strategy is registered for {kind.value}"
            ) from exc

    def validate_complete(self) -> None:
        missing = set(IdentityKind) - self._strategies.keys()
        if missing:
            kinds = ", ".join(sorted(kind.value for kind in missing))
            raise MissingIdentityStrategyError(
                f"Identity strategy registry is missing: {kinds}"
            )

    def registered_kinds(self) -> frozenset[IdentityKind]:
        return frozenset(self._strategies)


class OrganisationClassificationStrategyRegistry:
    """Maps each OrganisationClassification to its specialised strategy."""

    def __init__(
        self,
        strategies: Mapping[
            OrganisationClassification,
            OrganisationClassificationMatchingStrategy,
        ]
        | None = None,
    ):
        self._strategies: dict[
            OrganisationClassification,
            OrganisationClassificationMatchingStrategy,
        ] = {}
        for classification, strategy in (strategies or {}).items():
            self.register(classification, strategy)

    def register(
        self,
        classification: OrganisationClassification,
        strategy: OrganisationClassificationMatchingStrategy,
        *,
        replace: bool = False,
    ) -> None:
        if not isinstance(classification, OrganisationClassification):
            raise TypeError(
                "classification must be an OrganisationClassification"
            )
        if not callable(getattr(strategy, "compare", None)):
            raise TypeError("strategy must provide a callable compare method")
        if classification in self._strategies and not replace:
            raise ValueError(
                "A strategy is already registered for "
                f"{classification.value}"
            )
        self._strategies[classification] = strategy

    def get(
        self,
        classification: OrganisationClassification,
    ) -> OrganisationClassificationMatchingStrategy:
        if not isinstance(classification, OrganisationClassification):
            raise TypeError(
                "classification must be an OrganisationClassification"
            )
        try:
            return self._strategies[classification]
        except KeyError as exc:
            raise MissingOrganisationClassificationStrategyError(
                "No organisation matching strategy is registered for "
                f"{classification.value}"
            ) from exc

    def validate_complete(self) -> None:
        missing = set(OrganisationClassification) - self._strategies.keys()
        if missing:
            classifications = ", ".join(
                sorted(classification.value for classification in missing)
            )
            raise MissingOrganisationClassificationStrategyError(
                "Organisation classification strategy registry is missing: "
                f"{classifications}"
            )

    def registered_classifications(
        self,
    ) -> frozenset[OrganisationClassification]:
        return frozenset(self._strategies)


def build_default_identity_strategy_registry() -> IdentityStrategyRegistry:
    """Build the initial six-kind strategy registry."""

    from application.resolution.identity.strategies import (
        IndustryMatchingStrategy,
        OrganisationMatchingStrategy,
        PersonMatchingStrategy,
        PlaceMatchingStrategy,
        ProductMatchingStrategy,
        TechnologyMatchingStrategy,
    )

    classifications = build_default_organisation_classification_registry()
    registry = IdentityStrategyRegistry(
        {
            IdentityKind.PERSON: PersonMatchingStrategy(),
            IdentityKind.ORGANISATION: OrganisationMatchingStrategy(classifications),
            IdentityKind.PLACE: PlaceMatchingStrategy(),
            IdentityKind.INDUSTRY: IndustryMatchingStrategy(),
            IdentityKind.PRODUCT: ProductMatchingStrategy(),
            IdentityKind.TECHNOLOGY: TechnologyMatchingStrategy(),
        }
    )
    registry.validate_complete()
    return registry


def build_default_organisation_classification_registry(
) -> OrganisationClassificationStrategyRegistry:
    """Build the initial four-classification strategy registry."""

    from application.resolution.identity.strategies import (
        AcceleratorClassificationMatchingStrategy,
        IncubatorClassificationMatchingStrategy,
        InvestorClassificationMatchingStrategy,
        StartupClassificationMatchingStrategy,
    )

    registry = OrganisationClassificationStrategyRegistry(
        {
            OrganisationClassification.STARTUP: StartupClassificationMatchingStrategy(),
            OrganisationClassification.INVESTOR: InvestorClassificationMatchingStrategy(),
            OrganisationClassification.ACCELERATOR: AcceleratorClassificationMatchingStrategy(),
            OrganisationClassification.INCUBATOR: IncubatorClassificationMatchingStrategy(),
        }
    )
    registry.validate_complete()
    return registry
