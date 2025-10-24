"""Unit tests for :mod:`onyo.data.models`."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from onyo.data import (
    CorpusSnapshot,
    Ingredient,
    NutritionProfile,
    QuantityUnit,
    Recipe,
    RecipeIngredient,
)
from onyo.data.errors import ValidationReport


def build_catalog_ingredient(
    name: str,
    *,
    category: str | None = None,
    source_path: Path | None = None,
) -> Ingredient:
    """Create an Ingredient instance for tests."""
    return Ingredient(
        name=name,
        category=category,
        source_path=source_path,
    )


def build_recipe_ingredient(
    ingredient: Ingredient,
    *,
    quantity: float = 1.0,
    unit: QuantityUnit = QuantityUnit.GRAM,
    substitutes: tuple[Ingredient, ...] | None = None,
) -> RecipeIngredient:
    """Create a RecipeIngredient instance for tests."""
    return RecipeIngredient(
        ingredient=ingredient,
        quantity=quantity,
        unit=unit,
        substitutes=substitutes,
    )


def test_ingredient_with_relative_source_path_is_resolved() -> None:
    """Resolve relative ingredient paths to absolute ones."""
    ingredient_path = Path("ingredients/pantry.yaml")
    ingredient = Ingredient(
        name="Olive Oil",
        source_path=ingredient_path,
    )

    assert ingredient.source_path == ingredient_path.resolve()


def test_recipe_requires_absolute_source_path() -> None:
    """Resolve recipe source paths to absolute ones."""
    ingredient = build_catalog_ingredient("Carrot")

    recipe = Recipe(
        name="Test Recipe",
        portions=2,
        ingredients=(build_recipe_ingredient(ingredient),),
        source_path=Path("recipes/test.yaml"),
    )

    assert recipe.source_path.is_absolute()


def test_recipe_ingredients_cannot_be_empty() -> None:
    """Reject recipes that omit ingredient entries."""
    with pytest.raises(
        ValidationError,
        match="Tuple should have at least 1 item",
    ):
        Recipe(
            name="Empty Ingredients",
            portions=1,
            ingredients=(),
            source_path=Path("/recipes/empty.yaml"),
        )


def test_recipeingredient_substitutes_must_be_non_empty_tuple() -> None:
    """Require non-empty tuples when substitutes are provided."""
    carrot = build_catalog_ingredient("Carrot")
    parsnip = build_catalog_ingredient("Parsnip")

    with pytest.raises(
        ValidationError,
        match="Tuple should have at least 1 item",
    ):
        RecipeIngredient(
            ingredient=carrot,
            quantity=1.0,
            unit=QuantityUnit.GRAM,
            substitutes=(),
        )

    recipe_ingredient = RecipeIngredient(
        ingredient=carrot,
        quantity=1.0,
        unit=QuantityUnit.GRAM,
        substitutes=(parsnip,),
    )

    assert recipe_ingredient.substitutes == (parsnip,)


def test_recipeingredient_quantity_must_be_positive() -> None:
    """Reject zero or negative ingredient quantities."""
    carrot = build_catalog_ingredient("Carrot")

    with pytest.raises(ValidationError, match="greater than 0"):
        RecipeIngredient(
            ingredient=carrot,
            quantity=0,
            unit=QuantityUnit.GRAM,
        )


def test_nutrition_profile_accepts_partial_macros() -> None:
    """Allow nutrition profiles to omit optional macro fields."""
    profile = NutritionProfile(
        unit=QuantityUnit.GRAM,
        per_amount=100,
        protein=12.5,
    )

    assert profile.protein == 12.5
    assert profile.sugars is None


def test_nutrition_profile_requires_positive_amount() -> None:
    """Reject nutrition profiles with non-positive per-amount values."""
    with pytest.raises(ValidationError, match="greater than 0"):
        NutritionProfile(
            unit=QuantityUnit.GRAM,
            per_amount=0,
        )


def test_recipe_metadata_is_frozen() -> None:
    """Ensure recipe metadata cannot be mutated after creation."""
    ingredient = build_catalog_ingredient("Carrot")
    recipe = Recipe(
        name="Immutable Metadata",
        portions=2,
        ingredients=(build_recipe_ingredient(ingredient),),
        source_path=Path("/recipes/immutable.yaml"),
        metadata={"tags": ("vegan",)},
    )

    with pytest.raises(TypeError, match="mappingproxy"):
        recipe.metadata["tags"] = ("another",)  # type: ignore[attr-defined]


def test_models_are_immutable() -> None:
    """Prevent mutation of immutable model attributes."""
    ingredient = build_catalog_ingredient("Carrot")
    recipe_ingredient = build_recipe_ingredient(ingredient)
    recipe = Recipe(
        name="Immutable Recipe",
        portions=2,
        ingredients=(recipe_ingredient,),
        source_path=Path("/recipes/immutable.yaml"),
    )

    with pytest.raises(ValidationError, match="Instance is frozen"):
        recipe.name = "Mutated"
    with pytest.raises(ValidationError, match="Instance is frozen"):
        recipe_ingredient.quantity = 2.0
    with pytest.raises(ValidationError, match="Instance is frozen"):
        ingredient.name = "Mutated"


def test_recipe_optional_sections_accept_none() -> None:
    """Accept None for optional recipe sections."""
    ingredient = build_catalog_ingredient("Carrot")
    recipe = Recipe(
        name="Optional Sections",
        portions=2,
        ingredients=(build_recipe_ingredient(ingredient),),
        source_path=Path("/recipes/optional.yaml"),
        mise_en_place=None,
        method=None,
        metadata=None,
    )

    assert recipe.mise_en_place is None
    assert recipe.method is None
    assert recipe.metadata is None


def test_corpus_snapshot_collects_mappings() -> None:
    """Capture recipes, ingredients, and metadata within snapshots."""
    ingredient = build_catalog_ingredient(
        "Carrot",
        source_path=Path("/ingredients/vegetables.yaml"),
    )
    recipe = Recipe(
        name="Carrot Soup",
        portions=4,
        ingredients=(build_recipe_ingredient(ingredient),),
        source_path=Path("/recipes/carrot-soup.yaml"),
    )
    report = ValidationReport()
    generated_at = datetime.now(tz=UTC)
    snapshot = CorpusSnapshot(
        ingredients={"Carrot": ingredient},
        recipes={"Carrot Soup": recipe},
        validation_report=report,
        generated_at=generated_at,
    )

    assert snapshot.ingredients["Carrot"] is ingredient
    assert snapshot.recipes["Carrot Soup"] is recipe
    assert snapshot.validation_report is report
    assert snapshot.generated_at == generated_at
