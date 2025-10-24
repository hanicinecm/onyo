"""Immutable domain models representing the recipe corpus."""

from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field

from onyo.data.validators import freeze_mapping


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
    """Per-unit nutritional snapshot for an ingredient.

    Describes the nutritional content *in grams* per amount of the specified unit.

    As an example, a NutritionProfile(unit="piece", per_amount=3, protein=42.0)
    stored with an Ingredient(name="Egg") indicates that 3 eggs contain 42 g of protein.
    """

    # Required fields
    unit: QuantityUnit
    per_amount: Annotated[float, Field(gt=0)]

    # Optional fields
    sugars: Annotated[float | None, Field(gt=0)] = None
    protein: Annotated[float | None, Field(gt=0)] = None
    saturated_fat: Annotated[float | None, Field(gt=0)] = None
    unsaturated_fat: Annotated[float | None, Field(gt=0)] = None


class Ingredient(BaseModel, frozen=True):
    """An ingredient used in recipes."""

    # Required fields
    name: Annotated[str, Field(min_length=1)]

    # Optional fields
    category: Annotated[str | None, Field(min_length=1)] = None
    translations: Annotated[
        Mapping[LanguageCode, str] | None,
        Field(min_length=1),
        AfterValidator(freeze_mapping),
    ] = None
    nutrition: NutritionProfile | None = None
    source_path: Path | None = None
