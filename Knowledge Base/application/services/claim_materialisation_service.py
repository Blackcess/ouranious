"""Materialise accepted identity and relationship proposal Claims."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from pymysql.connections import Connection

from application.resolution.create_result import CreateAction, CreateResult
from application.resolution.identity.contracts import IdentityResolutionResult
from application.resolution.relationship.canonicalization import (
    canonicalize_relationship_properties,
)
from application.resolution.relationship.contracts import (
    RelationshipResolutionOutcome,
    RelationshipResolutionResult,
)
from application.services.create_orchestration import (
    resolve_and_create_identity_in_transaction,
    resolve_and_create_relationship_in_transaction,
)
from application.services.identity_resolution_service import IdentityResolutionService
from application.services.identity_resolver import IdentityResolver
from application.services.relationship_resolution_service import (
    RelationshipResolutionService,
)
from domain_models.Identity_model.identity import (
    Identity,
    IdentityKind,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Industry_model.industry import Industry
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator import Accelerator
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator_programme import AcceleratorProgramme, InvestmentTerms
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import (
    InvestmentStage,
    InvestmentTypes,
    Investor,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import (
    Startup,
    StartupBusinessModels,
    StartupStages,
)
from domain_models.Identity_model.Organisation_model.organisation import Organisation
from domain_models.Identity_model.Organisation_model.organisation_classification import OrganisationClassification
from domain_models.Identity_model.Person_model.person import Person
from domain_models.Identity_model.Place_model.place import Place, PlaceKind
from domain_models.Identity_model.Product_model.product import Product
from domain_models.Identity_model.Technology_model.technology import Technology
from domain_models.Provenance.claim import Claim, ClaimStatus
from domain_models.Provenance.materialisation import (
    ClaimMaterialisation,
    MaterialisationAction,
    MaterialisationOutcome,
    MaterialisationTargetKind,
)
from domain_models.Provenance.propositions import (
    IdentityProposalProposition,
    RelationshipProposition,
)
from domain_models.relationship_models.relationship import Relationship
from repositories.claim_materialisation_repository import ClaimMaterialisationRepository
from repositories.claim_repository import ClaimRepository
from repositories.relationship_repository import RelationshipRepository
from repositories.utils.errors import RepositoryNotFoundError
from infrastructure.database.connection import DatabaseManager
from utils.representations import Duration, DurationUnit, Money


class IdentitySaveRepository(Protocol):
    def save(self, identity: Identity, *, connection: Connection) -> None: ...


@dataclass(frozen=True)
class ClaimMaterialisationResult:
    claim_reference: UUID
    target_kind: MaterialisationTargetKind
    outcome: MaterialisationOutcome
    action: MaterialisationAction | None
    entity: Identity | Relationship | None
    override_applied: bool
    already_materialised: bool
    resolution: IdentityResolutionResult | RelationshipResolutionResult | None = None


class ClaimMaterialisationService:
    """Owns one transaction for Claim lock, canonical write, and Claim link."""

    def __init__(
        self,
        *,
        claim_repository: ClaimRepository,
        materialisation_repository: ClaimMaterialisationRepository,
        identity_repositories: dict[IdentityKind, IdentitySaveRepository],
        relationship_repository: RelationshipRepository,
        identity_resolver: IdentityResolver,
        identity_resolution_service: IdentityResolutionService,
        relationship_resolution_service: RelationshipResolutionService,
        database_manager: DatabaseManager,
    ):
        self._claim_repository = claim_repository
        self._materialisation_repository = materialisation_repository
        self._identity_repositories = identity_repositories
        self._relationship_repository = relationship_repository
        self._identity_resolver = identity_resolver
        self._identity_resolution_service = identity_resolution_service
        self._relationship_resolution_service = relationship_resolution_service
        self._database_manager = database_manager

    def materialise(
        self,
        claim_reference: UUID,
        *,
        allow_possible_duplicate: bool = False,
    ) -> ClaimMaterialisationResult:
        if not isinstance(claim_reference, UUID):
            raise TypeError("claim_reference must be a UUID")
        if not isinstance(allow_possible_duplicate, bool):
            raise TypeError("allow_possible_duplicate must be a boolean")

        with self._database_manager.transaction() as connection:
            claim = self._claim_repository.get_by_reference_for_update(
                claim_reference, connection=connection
            )
            if claim is None:
                raise RepositoryNotFoundError(f"Claim {claim_reference} does not exist.")

            prior = self._materialisation_repository.get_by_claim_reference(
                claim_reference, connection=connection
            )
            if prior is not None:
                entity = self._load_target(prior, connection=connection)
                return ClaimMaterialisationResult(
                    claim_reference=claim_reference,
                    target_kind=prior.target_kind,
                    outcome=prior.outcome,
                    action=prior.action,
                    entity=entity,
                    override_applied=prior.override_applied,
                    already_materialised=True,
                )

            if claim.status is not ClaimStatus.ACCEPTED:
                raise ValueError("Only accepted Claims can be materialised.")

            proposition = claim.proposition
            if isinstance(proposition, IdentityProposalProposition):
                result = self._materialise_identity(
                    claim, proposition, connection=connection,
                    allow_possible_duplicate=allow_possible_duplicate,
                )
            elif isinstance(proposition, RelationshipProposition):
                result = self._materialise_relationship(
                    claim, proposition, connection=connection,
                    allow_possible_duplicate=allow_possible_duplicate,
                )
            else:
                raise ValueError(
                    "This Claim proposition type is not enabled for materialisation yet."
                )

            if result.action is None or result.entity is None:
                return result

            record = ClaimMaterialisation(
                claim_reference=claim_reference,
                target_kind=result.target_kind,
                target_reference=(
                    result.entity.reference.value
                    if isinstance(result.entity, Identity)
                    else result.entity.get_reference().value
                ),
                outcome=result.outcome,
                action=result.action,
                override_applied=result.override_applied,
            )
            self._materialisation_repository.create(record, connection=connection)
            return result

    def _materialise_identity(
        self,
        claim: Claim,
        proposition: IdentityProposalProposition,
        *,
        connection: Connection,
        allow_possible_duplicate: bool,
    ) -> ClaimMaterialisationResult:
        identity = _build_identity(proposition)
        repository = self._identity_repositories.get(identity.kind)
        if repository is None:
            raise ValueError(f"No canonical repository is configured for {identity.kind.value}.")
        create_result = resolve_and_create_identity_in_transaction(
            identity,
            repository=repository,
            resolver=self._identity_resolution_service,
            allow_possible_duplicate=allow_possible_duplicate,
            connection=connection,
        )
        return _from_create_result(
            claim.reference,
            MaterialisationTargetKind.IDENTITY,
            create_result,
        )

    def _materialise_relationship(
        self,
        claim: Claim,
        proposition: RelationshipProposition,
        *,
        connection: Connection,
        allow_possible_duplicate: bool,
    ) -> ClaimMaterialisationResult:
        source = self._identity_resolver.get_by_id(
            proposition.source_reference, connection=connection
        )
        target = self._identity_resolver.get_by_id(
            proposition.target_reference, connection=connection
        )
        if source is None or target is None:
            missing = proposition.source_reference if source is None else proposition.target_reference
            raise RepositoryNotFoundError(f"Identity {missing.value} does not exist.")
        relationship = Relationship(
            source=source,
            target=target,
            type=proposition.relationship_type,
            properties=proposition.properties,
        )

        explicit_reference = proposition.existing_relationship_reference
        if explicit_reference is not None:
            existing = self._relationship_repository.get_by_id(
                explicit_reference, connection=connection
            )
            if existing is None:
                raise RepositoryNotFoundError(
                    f"Relationship {explicit_reference.value} does not exist."
                )
            if (
                existing.get_source().reference != proposition.source_reference
                or existing.get_target().reference != proposition.target_reference
                or existing.get_type() is not proposition.relationship_type
                or canonicalize_relationship_properties(existing)
                != canonicalize_relationship_properties(relationship)
            ):
                raise ValueError(
                    "The referenced relationship does not exactly match the proposed endpoints, type, and properties."
                )
            return ClaimMaterialisationResult(
                claim_reference=claim.reference,
                target_kind=MaterialisationTargetKind.RELATIONSHIP,
                outcome=MaterialisationOutcome.EXACT_MATCH,
                action=MaterialisationAction.LINKED,
                entity=existing,
                override_applied=False,
                already_materialised=False,
            )

        create_result = resolve_and_create_relationship_in_transaction(
            relationship,
            repository=self._relationship_repository,
            resolver=self._relationship_resolution_service,
            allow_possible_duplicate=allow_possible_duplicate,
            connection=connection,
        )
        return _from_create_result(
            claim.reference,
            MaterialisationTargetKind.RELATIONSHIP,
            create_result,
        )

    def _load_target(
        self, record: ClaimMaterialisation, *, connection: Connection
    ) -> Identity | Relationship:
        if record.target_kind is MaterialisationTargetKind.IDENTITY:
            entity = self._identity_resolver.get_by_id(
                record.target_reference, connection=connection
            )
        else:
            entity = self._relationship_repository.get_by_id(
                record.target_reference, connection=connection
            )
        if entity is None:
            raise RuntimeError("Materialisation record points to a missing canonical target.")
        return entity


def _from_create_result(claim_reference, target_kind, result):
    outcome = MaterialisationOutcome(result.outcome.value)
    if result.action is CreateAction.BLOCKED:
        return ClaimMaterialisationResult(
            claim_reference=claim_reference,
            target_kind=target_kind,
            outcome=outcome,
            action=None,
            entity=None,
            override_applied=False,
            already_materialised=False,
            resolution=result.resolution,
        )
    action = (
        MaterialisationAction.CREATED
        if result.action is CreateAction.CREATED
        else MaterialisationAction.LINKED
    )
    return ClaimMaterialisationResult(
        claim_reference=claim_reference,
        target_kind=target_kind,
        outcome=outcome,
        action=action,
        entity=result.entity,
        override_applied=result.override_applied,
        already_materialised=False,
        resolution=result.resolution,
    )


def _build_identity(proposition: IdentityProposalProposition) -> Identity:
    representations = IdentityRepresentations(
        canonical_name=proposition.canonical_name,
        aliases=set(proposition.aliases),
    )
    attributes = dict(proposition.attributes or {})
    kind = proposition.identity_kind

    if kind is IdentityKind.PERSON:
        _require_no_attributes(attributes, kind)
        return Person(representations=representations)
    if kind is IdentityKind.INDUSTRY:
        _require_no_attributes(attributes, kind)
        return Industry(representations=representations)
    if kind is IdentityKind.PRODUCT:
        _require_no_attributes(attributes, kind)
        return Product(representations=representations)
    if kind is IdentityKind.TECHNOLOGY:
        _require_no_attributes(attributes, kind)
        return Technology(representations=representations)
    if kind is IdentityKind.PLACE:
        if set(attributes) != {"place_kind"}:
            raise ValueError("PLACE proposals require only the 'place_kind' attribute.")
        return Place(
            representations=representations,
            place_kind=_as_enum(PlaceKind, attributes["place_kind"]),
        )
    if kind is IdentityKind.ORGANISATION:
        return _build_organisation(representations, attributes)
    raise ValueError(f"Unsupported identity kind: {kind!r}")


def _build_organisation(representations, attributes) -> Organisation:
    if set(attributes) != {"classifications"}:
        raise ValueError(
            "ORGANISATION proposals require a 'classifications' list of typed classification objects."
        )
    definitions = attributes["classifications"]
    if not isinstance(definitions, (list, tuple)) or not definitions:
        raise ValueError("Organisation classifications must be a non-empty list.")
    organisation = Organisation(
        representations=representations,
        classifications=set(),
    )
    seen_classifications = set()
    for definition in definitions:
        if not isinstance(definition, dict) or "classification" not in definition:
            raise TypeError("Each organisation classification must be an object with a classification field.")
        classification = _as_enum(OrganisationClassification, definition["classification"])
        if classification in seen_classifications:
            raise ValueError(f"Organisation classification {classification.value} was provided more than once.")
        seen_classifications.add(classification)
        values = {key: value for key, value in definition.items() if key != "classification"}
        if classification is OrganisationClassification.STARTUP:
            if set(values) != {"founding_year", "stage", "business_model"}:
                raise ValueError("Startup classification requires founding_year, stage, and business_model.")
            founding_year = _strict_int(values["founding_year"], "founding_year")
            if founding_year <= 0:
                raise ValueError("founding_year must be greater than zero.")
            model = Startup(
                founding_year=founding_year,
                stage=_as_enum(StartupStages, values["stage"]),
                business_model=_as_enum(StartupBusinessModels, values["business_model"]),
            )
        elif classification is OrganisationClassification.INVESTOR:
            if set(values) != {"investor_type", "investment_stage"}:
                raise ValueError("Investor classification requires investor_type and investment_stage.")
            model = Investor(
                investor_type=_as_enum(InvestmentTypes, values["investor_type"]),
                investment_stage=_as_enum(InvestmentStage, values["investment_stage"]),
            )
        elif classification is OrganisationClassification.ACCELERATOR:
            if set(values) != {"programmes"} or not isinstance(values["programmes"], list):
                raise ValueError("Accelerator classification requires a programmes list.")
            model = Accelerator()
            model.programmes.extend(_build_programme(item) for item in values["programmes"])
        elif classification is OrganisationClassification.INCUBATOR:
            if values:
                raise ValueError("Incubator classification does not accept additional attributes.")
            model = None
        else:
            raise ValueError(f"Unsupported organisation classification: {classification!r}")
        organisation.add_classification(classification)
        if model is not None:
            organisation.add_classification_model(classification, model)
    return organisation


def _build_programme(value) -> AcceleratorProgramme:
    if not isinstance(value, dict) or set(value) != {"name", "duration", "investment_terms"}:
        raise ValueError("Accelerator programme requires name, duration, and investment_terms.")
    duration = value["duration"]
    terms = value["investment_terms"]
    if (
        not isinstance(duration, dict)
        or not {"value", "unit"}.issubset(duration)
        or set(duration) - {"value", "unit", "start_date", "end_date"}
    ):
        raise ValueError("Programme duration has an invalid shape.")
    if not isinstance(terms, dict) or set(terms) != {"money", "equity_percentage"}:
        raise ValueError("Programme investment_terms has an invalid shape.")
    money = terms["money"]
    if not isinstance(money, dict) or set(money) != {"amount", "currency"}:
        raise ValueError("Programme money requires amount and currency.")
    name = value["name"]
    if not isinstance(name, str) or not name.strip() or len(name) > 255:
        raise ValueError("Programme name must contain 1 to 255 characters.")
    start_date = _as_date_or_none(duration.get("start_date"))
    end_date = _as_date_or_none(duration.get("end_date"))
    return AcceleratorProgramme(
        name=name,
        duration=Duration(
            value=_as_decimal(duration["value"], "duration.value"),
            unit=_as_enum(DurationUnit, duration["unit"]),
            start_date=start_date,
            end_date=end_date,
        ),
        investment_terms=InvestmentTerms(
            money=Money(
                amount=_as_decimal(money["amount"], "money.amount"),
                currency=money["currency"],
            ),
            equity_percentage=_as_decimal(terms["equity_percentage"], "equity_percentage"),
        ),
    )


def _require_no_attributes(attributes, kind):
    if attributes:
        raise ValueError(f"{kind.value} proposals do not accept additional attributes.")


def _as_enum(enum_type, value):
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {enum_type.__name__} value: {value!r}") from exc


def _strict_int(value, field_name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")
    return value


def _as_decimal(value, field_name):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise TypeError(f"{field_name} must be a decimal value.")
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"{field_name} is not a valid decimal.") from exc
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite.")
    return result


def _as_date_or_none(value):
    if value is None or (isinstance(value, date) and not isinstance(value, datetime)):
        return value
    if not isinstance(value, str):
        raise TypeError("Programme dates must be ISO date strings or null.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Programme dates must be ISO date strings.") from exc
