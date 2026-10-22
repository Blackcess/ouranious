"""Bounded candidate page shared by identity and relationship repositories."""

from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class CandidatePage(Generic[T]):
    items: tuple[T, ...]
    truncated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.truncated, bool):
            raise TypeError("truncated must be a boolean")
