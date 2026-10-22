from dataclasses import MISSING, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)
from domain_models.relationship_models.relationship_types.relationship_type_specification import (
    specification_registry,
)


def deserialize_relationship_properties(
    relationship_type: RelationshipType,
    payload: dict[str, Any] | None,
) -> object | None:
    """
    Convert a JSON properties object into the dataclass registered
    for the supplied relationship type.
    """

    specification = specification_registry.get(relationship_type)

    if specification is None:
        raise ValueError(
            f"Unsupported relationship type: {relationship_type}"
        )

    properties_type = specification.properties_type

    if properties_type is None:
        if payload is not None:
            if not isinstance(payload, dict):
                raise TypeError("Properties must be a JSON object")

            if payload:
                raise ValueError(
                    f"{relationship_type.value} does not accept properties"
                )

        return None

    if payload is None:
        raise ValueError(
            f"{relationship_type.value} requires properties"
        )

    if not isinstance(payload, dict):
        raise TypeError("Properties must be a JSON object")

    return _deserialize_dataclass(properties_type, payload)


def serialize_relationship_properties(
    relationship_type: RelationshipType,
    properties: object | None,
) -> dict[str, Any] | None:
    """
    Convert typed relationship properties into JSON-compatible data.
    """

    specification = specification_registry.get(relationship_type)

    if specification is None:
        raise ValueError(
            f"Unsupported relationship type: {relationship_type}"
        )

    expected_type = specification.properties_type

    if expected_type is None:
        if properties is not None:
            raise TypeError(
                f"{relationship_type.value} does not accept properties"
            )
        return None

    if not isinstance(properties, expected_type):
        raise TypeError(
            f"{relationship_type.value} requires "
            f"{expected_type.__name__}"
        )

    result = _serialize_value(properties)

    if not isinstance(result, dict):
        raise TypeError("Serialized properties must be a JSON object")

    return result


def _deserialize_dataclass(
    model_type: type,
    payload: dict[str, Any],
) -> object:
    if not is_dataclass(model_type):
        raise TypeError(
            f"Expected a dataclass type, got {model_type.__name__}"
        )

    model_fields = fields(model_type)
    known_names = {field.name for field in model_fields}
    unknown_names = set(payload) - known_names

    if unknown_names:
        raise ValueError(
            f"Unexpected properties for {model_type.__name__}: "
            f"{sorted(unknown_names)}"
        )

    type_hints = get_type_hints(model_type)
    values: dict[str, Any] = {}

    for model_field in model_fields:
        name = model_field.name

        if name not in payload:
            if (
                model_field.default is MISSING
                and model_field.default_factory is MISSING
            ):
                raise ValueError(
                    f"Missing required property '{name}' "
                    f"for {model_type.__name__}"
                )

            # Let the dataclass apply its declared default.
            continue

        values[name] = _deserialize_value(
            payload[name],
            type_hints.get(name, Any),
            field_name=name,
        )

    # The dataclass constructor and __post_init__ enforce domain
    # property constraints after type conversion.
    return model_type(**values)


def _deserialize_value(
    value: Any,
    expected_type: Any,
    *,
    field_name: str,
) -> Any:
    if expected_type is Any:
        return value

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # Handle Optional[T] and T | None.
    if origin in (Union, UnionType):
        if value is None and type(None) in args:
            return None

        errors: list[Exception] = []

        for candidate_type in args:
            if candidate_type is type(None):
                continue

            try:
                return _deserialize_value(
                    value,
                    candidate_type,
                    field_name=field_name,
                )
            except (TypeError, ValueError) as exc:
                errors.append(exc)

        raise ValueError(
            f"Invalid value for property '{field_name}'"
        ) from (errors[-1] if errors else None)

    if value is None:
        raise TypeError(
            f"Property '{field_name}' cannot be null"
        )

    if origin is list:
        if not isinstance(value, list):
            raise TypeError(f"Property '{field_name}' must be a list")

        item_type = args[0] if args else Any
        return [
            _deserialize_value(
                item,
                item_type,
                field_name=field_name,
            )
            for item in value
        ]

    if origin is set:
        if not isinstance(value, (list, set)):
            raise TypeError(
                f"Property '{field_name}' must be a list"
            )

        item_type = args[0] if args else Any
        return {
            _deserialize_value(
                item,
                item_type,
                field_name=field_name,
            )
            for item in value
        }

    if origin is dict:
        if not isinstance(value, dict):
            raise TypeError(
                f"Property '{field_name}' must be an object"
            )

        key_type, value_type = args if args else (Any, Any)

        return {
            _deserialize_value(
                key,
                key_type,
                field_name=field_name,
            ): _deserialize_value(
                item,
                value_type,
                field_name=field_name,
            )
            for key, item in value.items()
        }

    if isinstance(expected_type, type) and issubclass(
        expected_type, Enum
    ):
        try:
            return expected_type(value)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid enum value for property '{field_name}'"
            ) from exc

    if expected_type is Decimal:
        if isinstance(value, bool):
            raise TypeError(
                f"Property '{field_name}' must be a decimal"
            )

        if not isinstance(value, (str, int, float, Decimal)):
            raise TypeError(
                f"Property '{field_name}' must be a decimal"
            )

        try:
            result = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(
                f"Invalid decimal for property '{field_name}'"
            ) from exc

        if not result.is_finite():
            raise ValueError(
                f"Property '{field_name}' must be finite"
            )

        return result

    if expected_type is date:
        if not isinstance(value, str):
            raise TypeError(
                f"Property '{field_name}' must be an ISO date string"
            )

        try:
            result = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                f"Invalid ISO date for property '{field_name}'"
            ) from exc

        if isinstance(result, datetime):
            raise TypeError(
                f"Property '{field_name}' must be a date, not datetime"
            )

        return result

    if expected_type is bool:
        if type(value) is not bool:
            raise TypeError(
                f"Property '{field_name}' must be a boolean"
            )
        return value

    if expected_type is int:
        if type(value) is not int:
            raise TypeError(
                f"Property '{field_name}' must be an integer"
            )
        return value

    if expected_type is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(
                f"Property '{field_name}' must be numeric"
            )
        return float(value)

    if expected_type is str:
        if not isinstance(value, str):
            raise TypeError(
                f"Property '{field_name}' must be a string"
            )
        return value

    if isinstance(expected_type, type) and is_dataclass(expected_type):
        if not isinstance(value, dict):
            raise TypeError(
                f"Property '{field_name}' must be an object"
            )
        return _deserialize_dataclass(expected_type, value)

    if isinstance(expected_type, type) and isinstance(value, expected_type):
        return value

    raise TypeError(
        f"Unsupported or invalid type for property '{field_name}': "
        f"{expected_type}"
    )


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("Cannot serialize a non-finite Decimal")
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _serialize_value(
                getattr(value, field.name)
            )
            for field in fields(value)
        }

    if isinstance(value, dict):
        return {
            str(key): _serialize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set, frozenset)):
        return [_serialize_value(item) for item in value]

    if isinstance(value, (str, int, float, bool)):
        return value

    raise TypeError(
        f"Cannot serialize value of type {type(value).__name__}"
    )
