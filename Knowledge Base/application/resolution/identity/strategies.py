"""Strategy protocols for identity-kind and organisation-classification rules."""

from typing import TYPE_CHECKING, Protocol

from domain_models.Identity_model.Organisation_model.organisation import Organisation
from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)
from domain_models.Identity_model.identity import Identity, IdentityKind
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import (
    Startup,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import (
    Investor,
)

from application.resolution.identity.contracts import (
    CandidateComparison,
    CandidateMatchKind,
    MatchEvidence,
    MatchEvidenceStrength,
)
from utils.identity_names import normalize_identity_name

if TYPE_CHECKING:
    from application.resolution.identity.registry import (
        OrganisationClassificationStrategyRegistry,
    )


class IdentityMatchingStrategy(Protocol):
    """Compares two same-kind identities without accessing persistence."""

    def compare(
        self,
        identity: Identity,
        candidate: Identity,
    ) -> CandidateComparison:
        """Return a candidate-level classification with explanatory evidence."""
        ...


class OrganisationClassificationMatchingStrategy(Protocol):
    """Compares one classification's models as part of organisation matching."""

    def compare(
        self,
        *,
        classification: OrganisationClassification,
        identity: Organisation,
        candidate: Organisation,
    ) -> CandidateComparison:
        """Return evidence contributed by this classification, if any."""
        ...


class StrategyNotImplementedError(NotImplementedError):
    """Raised by registered scaffolding strategies until rules are implemented."""


class PendingIdentityStrategy:
    """Explicit registry entry for an identity kind whose rules are not wired yet."""

    def __init__(self, kind):
        self.kind = kind

    def compare(
        self,
        identity: Identity,
        candidate: Identity,
    ) -> CandidateComparison:
        raise StrategyNotImplementedError(
            f"Identity matching strategy for {self.kind.value} is not implemented"
        )


class PendingOrganisationClassificationStrategy:
    """Explicit entry for a classification whose matching rules are pending."""

    def __init__(self, classification: OrganisationClassification):
        self.classification = classification

    def compare(
        self,
        *,
        classification: OrganisationClassification,
        identity: Organisation,
        candidate: Organisation,
    ) -> CandidateComparison:
        raise StrategyNotImplementedError(
            "Organisation classification matching strategy for "
            f"{self.classification.value} is not implemented"
        )


class NameBasedIdentityStrategy:
    """Shared canonical-name and alias comparison for name-identified kinds."""

    def __init__(self, expected_kind: IdentityKind):
        self._expected_kind = expected_kind

    def compare(
        self,
        identity: Identity,
        candidate: Identity,
    ) -> CandidateComparison:
        if not isinstance(identity, Identity) or not isinstance(candidate, Identity):
            raise TypeError("identity and candidate must be Identity instances")
        if (
            identity.kind is not self._expected_kind
            or candidate.kind is not self._expected_kind
        ):
            return CandidateComparison(
                CandidateMatchKind.NON_MATCH,
                (
                    MatchEvidence(
                        rule="identity_kind_mismatch",
                        strength=MatchEvidenceStrength.CONFLICTING,
                        input_value=identity.kind,
                        candidate_value=candidate.kind,
                    ),
                ),
            )

        return _compare_representations(identity, candidate)


class PersonMatchingStrategy(NameBasedIdentityStrategy):
    def __init__(self):
        super().__init__(IdentityKind.PERSON)


class IndustryMatchingStrategy(NameBasedIdentityStrategy):
    def __init__(self):
        super().__init__(IdentityKind.INDUSTRY)


class ProductMatchingStrategy(NameBasedIdentityStrategy):
    def __init__(self):
        super().__init__(IdentityKind.PRODUCT)


class TechnologyMatchingStrategy(NameBasedIdentityStrategy):
    def __init__(self):
        super().__init__(IdentityKind.TECHNOLOGY)


class PlaceMatchingStrategy(NameBasedIdentityStrategy):
    """Name matching with PlaceKind consistency as an additional constraint."""

    def __init__(self):
        super().__init__(IdentityKind.PLACE)

    def compare(
        self,
        identity: Identity,
        candidate: Identity,
    ) -> CandidateComparison:
        from domain_models.Identity_model.Place_model.place import Place

        name_comparison = super().compare(identity, candidate)
        if name_comparison.kind is CandidateMatchKind.NON_MATCH:
            return name_comparison
        if not isinstance(identity, Place) or not isinstance(candidate, Place):
            raise TypeError("PLACE matching requires Place instances")

        input_place_kind = identity.get_place_kind()
        candidate_place_kind = candidate.get_place_kind()
        if input_place_kind == candidate_place_kind:
            return name_comparison

        evidence = name_comparison.evidence + (
            MatchEvidence(
                rule="place_kind_conflict",
                strength=MatchEvidenceStrength.CONFLICTING,
                input_value=input_place_kind,
                candidate_value=candidate_place_kind,
                detail="PlaceKind mismatch prevents an exact match.",
            ),
        )
        return CandidateComparison(CandidateMatchKind.POSSIBLE_DUPLICATE, evidence)


class StartupClassificationMatchingStrategy:
    """Uses populated Startup fields as consistency checks, not identifiers."""

    _fields = ("founding_year", "stage", "business_model")

    def compare(
        self,
        *,
        classification: OrganisationClassification,
        identity: Organisation,
        candidate: Organisation,
    ) -> CandidateComparison:
        left = identity.get_classification_model(classification)
        right = candidate.get_classification_model(classification)
        return _compare_model_fields(
            classification=classification,
            fields=self._fields,
            left=left,
            right=right,
            expected_type=Startup,
        )


class InvestorClassificationMatchingStrategy:
    """Uses populated investor attributes as consistency checks."""

    def compare(
        self,
        *,
        classification: OrganisationClassification,
        identity: Organisation,
        candidate: Organisation,
    ) -> CandidateComparison:
        left = identity.get_classification_model(classification)
        right = candidate.get_classification_model(classification)
        if left is None or right is None:
            return CandidateComparison(CandidateMatchKind.EXACT_MATCH)
        if not isinstance(left, Investor) or not isinstance(right, Investor):
            raise TypeError("INVESTOR classification requires Investor models")

        fields = (
            ("investor_type", left.get_investor_type(), right.get_investor_type()),
            ("investment_stage", left.get_investor_stage(), right.get_investor_stage()),
        )
        return _compare_values(classification, fields)


class AcceleratorClassificationMatchingStrategy:
    """Accelerator programmes have no stable identifier; they add no match key."""

    def compare(
        self,
        *,
        classification: OrganisationClassification,
        identity: Organisation,
        candidate: Organisation,
    ) -> CandidateComparison:
        return CandidateComparison(CandidateMatchKind.EXACT_MATCH)


class IncubatorClassificationMatchingStrategy:
    """Incubator is currently a placeholder model with no comparison fields."""

    def compare(
        self,
        *,
        classification: OrganisationClassification,
        identity: Organisation,
        candidate: Organisation,
    ) -> CandidateComparison:
        return CandidateComparison(CandidateMatchKind.EXACT_MATCH)


class OrganisationMatchingStrategy:
    """Combines shared representation matching with classification evidence."""

    def __init__(
        self,
        classification_strategies: "OrganisationClassificationStrategyRegistry",
    ):
        self._classification_strategies = classification_strategies

    def compare(
        self,
        identity: Identity,
        candidate: Identity,
    ) -> CandidateComparison:
        if not isinstance(identity, Organisation) or not isinstance(
            candidate, Organisation
        ):
            return CandidateComparison(CandidateMatchKind.NON_MATCH)

        base = _compare_representations(identity, candidate)
        classifications = identity.get_classifications() | candidate.get_classifications()
        for classification in sorted(classifications, key=lambda item: item.value):
            # Require explicit registration for every classification encountered.
            strategy = self._classification_strategies.get(classification)
            if (
                identity.has_classification(classification)
                and candidate.has_classification(classification)
            ):
                contribution = strategy.compare(
                    classification=classification,
                    identity=identity,
                    candidate=candidate,
                )
                base = _merge_organisation_evidence(base, contribution)
            else:
                base = _merge_organisation_evidence(
                    base,
                    CandidateComparison(
                        CandidateMatchKind.POSSIBLE_DUPLICATE,
                        (
                            MatchEvidence(
                                rule="organisation_classification_difference",
                                strength=MatchEvidenceStrength.CONFLICTING,
                                input_value=tuple(
                                    sorted(
                                        item.value
                                        for item in identity.get_classifications()
                                    )
                                ),
                                candidate_value=tuple(
                                    sorted(
                                        item.value
                                        for item in candidate.get_classifications()
                                    )
                                ),
                                detail=(
                                    "Classification differences are evidence, "
                                    "not proof of distinct organisations."
                                ),
                            ),
                        ),
                    ),
                )
        return base


def _compare_representations(
    identity: Identity,
    candidate: Identity,
) -> CandidateComparison:
    input_name = normalize_identity_name(
        identity.representations.canonical_name
    )
    candidate_name = normalize_identity_name(
        candidate.representations.canonical_name
    )
    input_aliases = _normalized_aliases(identity.representations.aliases)
    candidate_aliases = _normalized_aliases(candidate.representations.aliases)

    evidence: list[MatchEvidence] = []
    deterministic = False

    if input_name and input_name == candidate_name:
        deterministic = True
        evidence.append(
            MatchEvidence(
                rule="canonical_name_equal",
                strength=MatchEvidenceStrength.DETERMINISTIC,
                input_value=identity.representations.canonical_name,
                candidate_value=candidate.representations.canonical_name,
            )
        )
    if input_name and input_name in candidate_aliases:
        deterministic = True
        evidence.append(
            MatchEvidence(
                rule="input_canonical_matches_candidate_alias",
                strength=MatchEvidenceStrength.DETERMINISTIC,
                input_value=identity.representations.canonical_name,
                candidate_value=candidate_aliases[input_name],
            )
        )
    if candidate_name and candidate_name in input_aliases:
        deterministic = True
        evidence.append(
            MatchEvidence(
                rule="input_alias_matches_candidate_canonical",
                strength=MatchEvidenceStrength.DETERMINISTIC,
                input_value=input_aliases[candidate_name],
                candidate_value=candidate.representations.canonical_name,
            )
        )

    alias_overlap = input_aliases.keys() & candidate_aliases.keys()
    if alias_overlap:
        evidence.extend(
            MatchEvidence(
                rule="alias_to_alias_equal",
                strength=MatchEvidenceStrength.SUPPORTING,
                input_value=input_aliases[alias],
                candidate_value=candidate_aliases[alias],
            )
            for alias in sorted(alias_overlap)
        )

    if deterministic:
        kind = CandidateMatchKind.EXACT_MATCH
    elif alias_overlap:
        kind = CandidateMatchKind.POSSIBLE_DUPLICATE
    else:
        kind = CandidateMatchKind.NON_MATCH
    return CandidateComparison(kind, tuple(evidence))


def _normalized_aliases(aliases: set[str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for alias in sorted(aliases):
        key = normalize_identity_name(alias)
        if key:
            normalized.setdefault(key, alias)
    return normalized


def _compare_model_fields(
    *,
    classification: OrganisationClassification,
    fields: tuple[str, ...],
    left: object | None,
    right: object | None,
    expected_type: type,
) -> CandidateComparison:
    if left is None or right is None:
        return CandidateComparison(CandidateMatchKind.EXACT_MATCH)
    if not isinstance(left, expected_type) or not isinstance(right, expected_type):
        raise TypeError(
            f"{classification.value} classification has an invalid model type"
        )
    values = tuple((name, getattr(left, name), getattr(right, name)) for name in fields)
    return _compare_values(classification, values)


def _compare_values(
    classification: OrganisationClassification,
    values: tuple[tuple[str, object | None, object | None], ...],
) -> CandidateComparison:
    evidence: list[MatchEvidence] = []
    has_conflict = False
    for field_name, left_value, right_value in values:
        if left_value is None or right_value is None:
            continue
        equal = left_value == right_value
        has_conflict |= not equal
        evidence.append(
            MatchEvidence(
                rule=f"{classification.value}_{field_name}_{'equal' if equal else 'conflict'}",
                strength=(
                    MatchEvidenceStrength.SUPPORTING
                    if equal
                    else MatchEvidenceStrength.CONFLICTING
                ),
                input_value=left_value,
                candidate_value=right_value,
            )
        )
    return CandidateComparison(
        CandidateMatchKind.POSSIBLE_DUPLICATE
        if has_conflict
        else CandidateMatchKind.EXACT_MATCH,
        tuple(evidence),
    )


def _merge_organisation_evidence(
    base: CandidateComparison,
    contribution: CandidateComparison,
) -> CandidateComparison:
    evidence = base.evidence + contribution.evidence
    if base.kind is CandidateMatchKind.NON_MATCH:
        return CandidateComparison(CandidateMatchKind.NON_MATCH, evidence)
    if (
        base.kind is CandidateMatchKind.POSSIBLE_DUPLICATE
        or contribution.kind is CandidateMatchKind.POSSIBLE_DUPLICATE
        or any(item.strength is MatchEvidenceStrength.CONFLICTING for item in evidence)
    ):
        return CandidateComparison(CandidateMatchKind.POSSIBLE_DUPLICATE, evidence)
    return CandidateComparison(base.kind, evidence)
