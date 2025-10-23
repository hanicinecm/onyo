"""Immutable domain models representing the recipe corpus."""

from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class QuantityUnit(str, Enum):
    """Supported measurement units for recipe quantities."""

    GRAM = "g"
    KILOGRAM = "kg"
    MILLILITRE = "ml"
    LITRE = "l"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    PIECE = "piece"


class LanguageCode(str, Enum):
    """Supported language codes for ingredient translations."""

    DE = "de"
    CZ = "cz"


class NutritionProfile(BaseModel, frozen=True):
    """Per-unit nutritional snapshot for an ingredient."""

    unit: QuantityUnit
    per_amount: Annotated[float, Field(gt=0)]
    sugars: Annotated[float | None, Field(gt=0)] = None
    protein: Annotated[float | None, Field(gt=0)] = None
    saturated_fat: Annotated[float | None, Field(gt=0)] = None
    unsaturated_fat: Annotated[float | None, Field(gt=0)] = None


class Ingredient(BaseModel, frozen=True):
    """An ingredient used in recipes."""

    name: Annotated[str, Field(min_length=1)]
    category: Annotated[str | None, Field(min_length=1)] = None
    translations: Mapping[LanguageCode, str] | None = None
    nutrition: NutritionProfile | None = None
    source_path: Path | None = None
    recipes: tuple[str, ...] = ()

    @field_validator("translations")
    @classmethod
    def _freeze_translations(
        cls, value: Mapping[str, str] | None
    ) -> Mapping[str, str] | None:
        """Ensure translations are stored as an immutable mapping."""
        if value is None:
            return None
        return MappingProxyType(dict(value))

    @field_validator("recipes")
    @classmethod
    def _unique_recipes(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        if len(v) != len(set(v)):
            msg = "Duplicate recipes for one ingredient."
            raise ValueError(msg)
        return v
