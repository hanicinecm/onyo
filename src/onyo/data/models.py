"""Immutable domain models representing the recipe corpus."""

from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from onyo.data.errors import ValidationReport
from onyo.data.validators import freeze_mapping, resolve_path


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


class FrozenStrictModel(BaseModel):
    """Base model enforcing immutability and strict field validation."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
    )


class NutritionProfile(FrozenStrictModel):
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


class Ingredient(FrozenStrictModel):
    """Catalog entry describing a single ingredient.

    When loaded from the catalog, contains the source file path and might include
    optional category, name translations and per-unit nutrition information.

    If instantiated as an ephemeral ingredient (not present in the catalog), only
    the name field will be populated.
    """

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
    source_path: Annotated[Path | None, AfterValidator(resolve_path)] = None


class RecipeIngredient(FrozenStrictModel):
    """A resolved ingredient reference within a recipe.

    Stores the ingredient instance, the quantity and unit used in the recipe,
    and an optional non-empty set of possible substitute ingredients.
    """

    # Required fields
    ingredient: Ingredient
    quantity: Annotated[float, Field(gt=0)]
    unit: QuantityUnit

    # Optional fields
    substitutes: Annotated[tuple[Ingredient, ...] | None, Field(min_length=1)] = None


class Recipe(FrozenStrictModel):
    """Primary recipe model assembled from corpus YAML files.

    Includes the immutable ingredient list, number of cooking portions, and the source
    file path.

    Optionally includes description, mise en place and method steps, and arbitrary
    metadata.
    """

    # Required fields
    name: Annotated[str, Field(min_length=1)]
    portions: Annotated[int, Field(gt=0)]
    ingredients: Annotated[tuple[RecipeIngredient, ...], Field(min_length=1)]
    source_path: Annotated[Path, AfterValidator(resolve_path)]

    # Optional fields
    description: Annotated[str | None, Field(min_length=1)] = None
    mise_en_place: Annotated[tuple[str, ...] | None, Field(min_length=1)] = None
    method: Annotated[tuple[str, ...] | None, Field(min_length=1)] = None
    metadata: Annotated[
        Mapping[str, Any] | None,
        Field(min_length=1),
        AfterValidator(freeze_mapping),
    ] = None


class CorpusSnapshot(FrozenStrictModel):
    """Immutable aggregation of recipes, ingredients, and validation diagnostics.

    Represents the outcome of a corpus load, keeping the resolved ingredient and
    recipe mappings keyed by their names, the validation report emitted during the
    load, and the timestamp recording when the snapshot was generated.
    """

    recipes: Annotated[Mapping[str, Recipe], AfterValidator(freeze_mapping)]
    ingredients: Annotated[Mapping[str, Ingredient], AfterValidator(freeze_mapping)]
    validation_report: ValidationReport
    generated_at: datetime
