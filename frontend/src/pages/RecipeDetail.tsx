import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api } from "../api/client";
import type { Recipe } from "../api/types";

export function RecipeDetailPage() {
  const { recipeId } = useParams();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!recipeId) {
      return;
    }
    void api
      .getRecipe(Number(recipeId))
      .then(setRecipe)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Recipe not found");
      });
  }, [recipeId]);

  if (error) {
    return (
      <section className="panel">
        <p className="error">{error}</p>
        <Link to="/recipes">Back to recipes</Link>
      </section>
    );
  }

  if (!recipe) {
    return <p>Loading…</p>;
  }

  return (
    <section className="panel">
      <p className="eyebrow">
        <Link to="/recipes">Recipes</Link>
      </p>
      <h2>{recipe.name}</h2>
      {recipe.description ? <p className="lede">{recipe.description}</p> : null}
      <p>
        Makes {recipe.servings} serving{recipe.servings === 1 ? "" : "s"}
      </p>
      <h3>Ingredients</h3>
      {recipe.ingredients.length === 0 ? (
        <p className="empty">No ingredients on this recipe.</p>
      ) : (
        <ul className="plain-list">
          {recipe.ingredients.map((item) => (
            <li key={item.ingredient_id}>
              {item.quantity_g} g {item.name}
            </li>
          ))}
        </ul>
      )}
      {recipe.instructions ? (
        <>
          <h3>Instructions</h3>
          <p className="prewrap">{recipe.instructions}</p>
        </>
      ) : null}
    </section>
  );
}
