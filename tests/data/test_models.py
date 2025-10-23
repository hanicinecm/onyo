# ruff: noqa: D103, S101, PGH003

"""Unit tests for :mod:`onyo.data.models`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from onyo.data import (
    Ingredient,
    NutritionProfile,
    QuantityUnit,
    Recipe,
    RecipeIngredient,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def ingredient_carrot() -> Ingredient:
    return Ingredient(name="Carrot")


@pytest.fixture
def ingredient_onion() -> Ingredient:
    return Ingredient(name="Onion")


@pytest.fixture
def ingredient_oil() -> Ingredient:
    return Ingredient(
        name="Olive Oil",
        nutrition=NutritionProfile(
            unit=QuantityUnit.TABLESPOON,
            per_amount=1.0,
        ),
        recipes=("Roasted Carrots",),
        translations={"pl": "Oliwa"},
    )


def test_recipe_normalises_iterables(
    ingredient_carrot: Ingredient, ingredient_onion: Ingredient, tmp_path: Path
) -> None:
    base = RecipeIngredient(
        ingredient=ingredient_carrot,
        quantity=2,
        unit=QuantityUnit.PIECE,
        substitutes=[ingredient_onion],  # type: ignore
    )

    recipe = Recipe(
        name="Roasted Carrots",
        portions=4,
        ingredients=[base],  # type: ignore
        source_path=tmp_path / "roasted-carrots.yaml",
        mise_en_place=["Peel carrots"],  # type: ignore
        method=["Roast"],  # type: ignore
    )

    assert isinstance(recipe.ingredients, tuple)
    assert recipe.ingredients[0].substitutes == (ingredient_onion,)
    assert recipe.mise_en_place == ("Peel carrots",)
    assert recipe.method == ("Roast",)
    assert recipe.ingredient_names == ("Carrot",)


def test_recipe_rejects_duplicate_ingredient_names(
    ingredient_carrot: Ingredient, tmp_path: Path
) -> None:
    duplicate = RecipeIngredient(
        ingredient=ingredient_carrot,
        quantity=1,
        unit=QuantityUnit.PIECE,
    )

    with pytest.raises(ValueError, match="at most once"):
        Recipe(
            name="Duplicate Ingredient Recipe",
            portions=2,
            ingredients=(duplicate, duplicate),
            source_path=tmp_path / "duplicate.yaml",
        )


def test_recipe_index_by_name_rejects_duplicates(
    ingredient_carrot: Ingredient, tmp_path: Path
) -> None:
    recipe_a = Recipe(
        name="Shared Name",
        portions=2,
        ingredients=(
            RecipeIngredient(
                ingredient=ingredient_carrot,
                quantity=1,
                unit=QuantityUnit.PIECE,
            ),
        ),
        source_path=tmp_path / "a.yaml",
    )

    recipe_b = Recipe(
        name="Shared Name",
        portions=3,
        ingredients=(
            RecipeIngredient(
                ingredient=ingredient_carrot,
                quantity=2,
                unit=QuantityUnit.PIECE,
            ),
        ),
        source_path=tmp_path / "b.yaml",
    )

    with pytest.raises(ValueError, match="Duplicate recipe name"):
        Recipe.index_by_name([recipe_a, recipe_b])


def test_recipe_index_by_name_returns_mapping(
    ingredient_carrot: Ingredient, tmp_path: Path
) -> None:
    recipe = Recipe(
        name="Unique Name",
        portions=2,
        ingredients=(
            RecipeIngredient(
                ingredient=ingredient_carrot,
                quantity=1,
                unit=QuantityUnit.PIECE,
            ),
        ),
        source_path=tmp_path / "unique.yaml",
    )

    index = Recipe.index_by_name([recipe])

    assert index["Unique Name"] is recipe


def test_recipe_requires_positive_portions(
    ingredient_carrot: Ingredient, tmp_path: Path
) -> None:
    with pytest.raises(ValueError, match="must be positive"):
        Recipe(
            name="Invalid Portions",
            portions=0,
            ingredients=(
                RecipeIngredient(
                    ingredient=ingredient_carrot,
                    quantity=1,
                    unit=QuantityUnit.PIECE,
                ),
            ),
            source_path=tmp_path / "invalid.yaml",
        )


def test_recipe_metadata_must_be_mapping(
    ingredient_carrot: Ingredient, tmp_path: Path
) -> None:
    with pytest.raises(TypeError, match="must be a mapping"):
        Recipe(
            name="Bad Metadata",
            portions=1,
            ingredients=(
                RecipeIngredient(
                    ingredient=ingredient_carrot,
                    quantity=1,
                    unit=QuantityUnit.PIECE,
                ),
            ),
            source_path=tmp_path / "metadata.yaml",
            metadata=[("key", "value")],  # type: ignore[arg-type]
        )


def test_recipe_requires_name(ingredient_carrot: Ingredient, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        Recipe(
            name="",
            portions=1,
            ingredients=(
                RecipeIngredient(
                    ingredient=ingredient_carrot,
                    quantity=1,
                    unit=QuantityUnit.PIECE,
                ),
            ),
            source_path=tmp_path / "empty-name.yaml",
        )


def test_recipeingredient_quantity_coercion(ingredient_carrot: Ingredient) -> None:
    entry = RecipeIngredient(
        ingredient=ingredient_carrot,
        quantity=2,
        unit=QuantityUnit.TABLESPOON,
    )

    assert entry.quantity == 2.0


def test_ingredient_normalises_translations_and_recipes(
    ingredient_oil: Ingredient,
) -> None:
    assert ingredient_oil.translations["pl"] == "Oliwa"
    assert ingredient_oil.recipes == ("Roasted Carrots",)
    with pytest.raises(TypeError):
        ingredient_oil.translations["en"] = "Oil"  # type: ignore[index]


def test_ingredient_index_by_name_rejects_duplicates(
    ingredient_carrot: Ingredient,
) -> None:
    with pytest.raises(ValueError, match="Duplicate ingredient name"):
        Ingredient.index_by_name([ingredient_carrot, ingredient_carrot])


def test_recipeingredient_unit_must_match_nutrition(
    ingredient_oil: Ingredient,
) -> None:
    with pytest.raises(ValueError, match="must match"):
        RecipeIngredient(
            ingredient=ingredient_oil,
            quantity=1,
            unit=QuantityUnit.PIECE,
        )


def test_ingredient_requires_name() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        Ingredient(name="")


def test_ingredient_index_by_name_returns_mapping(
    ingredient_carrot: Ingredient,
) -> None:
    index = Ingredient.index_by_name([ingredient_carrot])

    assert index["Carrot"] is ingredient_carrot


def test_nutrition_profile_coerces_numeric_fields() -> None:
    profile = NutritionProfile(
        unit=QuantityUnit.GRAM,
        per_amount="100",  # type: ignore
        sugars="4.5",  # type: ignore
        protein=1,
        saturated_fat=None,
        unsaturated_fat="3.2",  # type: ignore
    )

    assert profile.per_amount == 100.0
    assert profile.sugars == 4.5
    assert profile.protein == 1.0
    assert profile.saturated_fat is None
    assert profile.unsaturated_fat == 3.2
