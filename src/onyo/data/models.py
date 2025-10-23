"""Immutable domain models representing the recipe corpus."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime
    from pathlib import Path

    from .errors import ValidationReport


def _coerce_float(value: float | str, field_name: str) -> float:
    """Coerce *value* to float, raising ``TypeError`` on failure."""
    if isinstance(value, bool):  # pragma: no cover - defensive guard
        msg = f"{field_name} must be numeric"
        raise TypeError(msg)

    try:
        return float(value)
    except (TypeError, ValueError) as error:  # pragma: no cover - defensive guard
        msg = f"{field_name} must be coercible to float"
        raise TypeError(msg) from error


class QuantityUnit(str, Enum):
    """Supported measurement units for recipe quantities."""

    GRAM = "g"
    KILOGRAM = "kg"
    MILLILITRE = "ml"
    LITRE = "l"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    PIECE = "piece"


@dataclass(frozen=True, slots=True)
class Recipe:
    """Persistent representation of a recipe."""

    name: str
    portions: int
    ingredients: tuple[RecipeIngredient, ...]
    source_path: Path
    description: str | None = None
    mise_en_place: tuple[str, ...] = ()
    method: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    ingredient_names: tuple[str, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate and normalise recipe state post-initialisation."""
        if not self.name:
            msg = "Recipe.name must not be empty"
            raise ValueError(msg)
        if self.portions <= 0:
            msg = "Recipe.portions must be positive"
            raise ValueError(msg)

        normalized_ingredients = tuple(self.ingredients)
        for entry in normalized_ingredients:
            if not isinstance(entry, RecipeIngredient):
                msg = "Recipe.ingredients must contain RecipeIngredient instances"
                raise TypeError(msg)

        ingredient_names = tuple(ri.ingredient.name for ri in normalized_ingredients)
        if len(set(ingredient_names)) != len(ingredient_names):
            msg = "Recipe.ingredients must reference each ingredient at most once"
            raise ValueError(msg)

        object.__setattr__(self, "ingredients", normalized_ingredients)
        object.__setattr__(self, "ingredient_names", ingredient_names)
        object.__setattr__(self, "mise_en_place", tuple(self.mise_en_place))
        object.__setattr__(self, "method", tuple(self.method))

        if not isinstance(self.metadata, Mapping):
            msg = "Recipe.metadata must be a mapping"
            raise TypeError(msg)

    @staticmethod
    def index_by_name(recipes: Iterable[Recipe]) -> dict[str, Recipe]:
        """Build a lookup table of recipes by unique name."""
        index: dict[str, Recipe] = {}
        for recipe in recipes:
            if recipe.name in index:
                msg = f"Duplicate recipe name detected: {recipe.name}"
                raise ValueError(msg)
            index[recipe.name] = recipe
        return index


@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    """Usage of an ingredient within a recipe."""

    ingredient: Ingredient
    quantity: float
    unit: QuantityUnit
    substitutes: tuple[Ingredient, ...] = ()

    def __post_init__(self) -> None:
        """Normalise substitute collection and quantity representation."""
        normalized_substitutes = tuple(self.substitutes)
        for substitute in normalized_substitutes:
            if not isinstance(substitute, Ingredient):  # pragma: no cover - type guard
                msg = "RecipeIngredient.substitutes must contain Ingredient instances"
                raise TypeError(msg)

        object.__setattr__(self, "substitutes", normalized_substitutes)

        raw_quantity = self.quantity
        if isinstance(raw_quantity, bool):  # pragma: no cover - defensive guard
            msg = "RecipeIngredient.quantity must be numeric"
            raise TypeError(msg)

        try:
            coerced_quantity = float(raw_quantity)
        except (TypeError, ValueError) as error:  # pragma: no cover - defensive
            msg = "RecipeIngredient.quantity must be coercible to float"
            raise TypeError(msg) from error

        object.__setattr__(self, "quantity", coerced_quantity)

        nutrition = self.ingredient.nutrition
        if nutrition is not None and nutrition.unit is not self.unit:
            msg = (
                "RecipeIngredient.unit must match the nutrition profile unit of "
                f"{self.ingredient.name}"
            )
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class Ingredient:
    """Shared ingredient metadata sourced from the corpus."""

    name: str
    category: str | None = None
    translations: Mapping[str, str] = field(default_factory=dict)
    nutrition: NutritionProfile | None = None
    source_path: Path | None = None
    recipes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Normalise optional fields and guard against duplicate references."""
        if not self.name:
            msg = "Ingredient.name must not be empty"
            raise ValueError(msg)

        translations_proxy = MappingProxyType(dict(self.translations))
        object.__setattr__(self, "translations", translations_proxy)

        normalized_recipes = tuple(self.recipes)
        if len(set(normalized_recipes)) != len(normalized_recipes):
            msg = "Ingredient.recipes must list each recipe at most once"
            raise ValueError(msg)
        object.__setattr__(self, "recipes", normalized_recipes)

        if self.nutrition is not None and not isinstance(
            self.nutrition, NutritionProfile
        ):
            msg = "Ingredient.nutrition must be a NutritionProfile instance"
            raise TypeError(msg)

    @staticmethod
    def index_by_name(ingredients: Iterable[Ingredient]) -> dict[str, Ingredient]:
        """Build a lookup table of ingredients by unique name."""
        index: dict[str, Ingredient] = {}
        for ingredient in ingredients:
            key = ingredient.name
            if key in index:
                msg = f"Duplicate ingredient name detected: {key}"
                raise ValueError(msg)
            index[key] = ingredient
        return index


@dataclass(frozen=True, slots=True)
class NutritionProfile:
    """Per-unit nutritional snapshot for an ingredient."""

    unit: QuantityUnit
    per_amount: float
    sugars: float | None = None
    protein: float | None = None
    saturated_fat: float | None = None
    unsaturated_fat: float | None = None

    def __post_init__(self) -> None:
        """Coerce numeric fields to float for consistent downstream usage."""
        object.__setattr__(
            self,
            "per_amount",
            _coerce_float(self.per_amount, "per_amount"),
        )
        for field_name in ("sugars", "protein", "saturated_fat", "unsaturated_fat"):
            value = getattr(self, field_name)
            if value is None:
                continue
            object.__setattr__(self, field_name, _coerce_float(value, field_name))


@dataclass(frozen=True, slots=True)
class CorpusSnapshot:
    """A complete, validated view of the recipe corpus."""

    recipes: Mapping[str, Recipe]
    ingredients: Mapping[str, Ingredient]
    validation_report: ValidationReport | None
    generated_at: datetime
