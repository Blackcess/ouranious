"""Canonical, type-aware keys for registered relationship properties."""

from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from collections.abc import Mapping, Set

from domain_models.relationship_models.relationship import Relationship
from domain_models.relationship_models.relationship_types.relationship_type_specification import (
    specification_registry,
)


def canonicalize_relationship_properties(
    relationship: Relationship,
) -> tuple:
    """Canonicalize properties using the type model in the existing registry.

    Propertyless relationship types use the empty tuple. The Relationship
    constructor already validates endpoint kinds and property model types; this
    function consults the same specification to identify propertyless types and
    rejects malformed or unsupported objects explicitly.
    """

    if not isinstance(relationship, Relationship):
        raise TypeError("relationship must be a Relationship instance")
    relationship_type = relationship.get_type()
    specification = specification_registry.get(relationship_type)
    if specification is None:
        raise ValueError(f"Unsupported relationship type: {relationship_type}")

    properties_type = specification.properties_type
    properties = relationship.get_properties()
    if properties_type is None:
        if properties is not None:
            raise TypeError(
                f"{relationship_type.value} does not accept relationship properties"
            )
        return ()
    if not isinstance(properties, properties_type):
        raise TypeError(
            f"{relationship_type.value} requires {properties_type.__name__}"
        )
    return _canonicalize(properties)


def compare_canonical_properties(
    left: tuple,
    right: tuple,
) -> tuple[bool, tuple[str, ...]]:
    """Return (has_conflict, missing-value paths) for candidate properties."""

    conflicts: list[str] = []
    missing: list[str] = []
    _compare_values(left, right, path="properties", conflicts=conflicts, missing=missing)
    return bool(conflicts), tuple(sorted(set(missing)))


def _canonicalize(value: object) -> tuple:
    if value is None:
        return ("none",)
    if isinstance(value, Enum):
        return (
            "enum",
            _qualified_type(value),
            _canonicalize(value.value),
        )
    if isinstance(value, datetime):
        return ("datetime", value.isoformat(), value.fold)
    if isinstance(value, date):
        return ("date", value.isoformat())
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("relationship property Decimal values must be finite")
        sign, digits, exponent = value.as_tuple()
        digits = list(digits)
        if not any(digits):
            return ("decimal", 0, (0,), 0)
        while digits and digits[-1] == 0:
            digits.pop()
            exponent += 1
        return ("decimal", sign, tuple(digits), exponent)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("relationship property float values must be finite")
        return ("float", value.hex())
    if isinstance(value, str):
        return ("str", value)
    if isinstance(value, bytes):
        return ("bytes", value)
    if is_dataclass(value) and not isinstance(value, type):
        return (
            "dataclass",
            _qualified_type(value),
            tuple(
                (field.name, _canonicalize(getattr(value, field.name)))
                for field in fields(value)
            ),
        )
    if isinstance(value, Mapping):
        entries = [(_canonicalize(key), _canonicalize(item)) for key, item in value.items()]
        return ("mapping", _qualified_type(value), tuple(sorted(entries, key=repr)))
    if isinstance(value, Set) and not isinstance(value, (str, bytes)):
        return (
            "set",
            _qualified_type(value),
            tuple(sorted((_canonicalize(item) for item in value), key=repr)),
        )
    if isinstance(value, (tuple, list)):
        return (
            "sequence",
            _qualified_type(value),
            tuple(_canonicalize(item) for item in value),
        )
    raise TypeError(
        f"Unsupported relationship property value type: {_qualified_type(value)}"
    )


def _compare_values(
    left: tuple,
    right: tuple,
    *,
    path: str,
    conflicts: list[str],
    missing: list[str],
) -> None:
    if left == right:
        return
    if left[0] == "none" or right[0] == "none":
        missing.append(path)
        return
    if (
        left[0] == right[0] == "dataclass"
        and left[1] == right[1]
    ):
        left_fields = dict(left[2])
        right_fields = dict(right[2])
        if left_fields.keys() != right_fields.keys():
            conflicts.append(path)
            return
        for field_name in left_fields:
            _compare_values(
                left_fields[field_name],
                right_fields[field_name],
                path=f"{path}.{field_name}",
                conflicts=conflicts,
                missing=missing,
            )
        return
    conflicts.append(path)


def _qualified_type(value: object) -> str:
    value_type = type(value)
    return f"{value_type.__module__}.{value_type.__qualname__}"
