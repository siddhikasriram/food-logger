import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { api } from "../api/client";
import type { Ingredient, Recipe } from "../api/types";
import { useUser } from "../context/UserContext";

type Row = { ingredient_id: string; quantity_g: string };

export function RecipesPage() {
  const { userId } = useUser();
  const navigate = useNavigate();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [rows, setRows] = useState<Row[]>([{ ingredient_id: "", quantity_g: "100" }]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function reload() {
    const [nextRecipes, nextIngredients] = await Promise.all([
      api.listRecipes(),
      api.listIngredients(),
    ]);
    setRecipes(nextRecipes);
    setIngredients(nextIngredients);
  }

  useEffect(() => {
    void reload().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "Could not load recipes");
    });
  }, []);

  async function onCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const selected = rows
      .filter((row) => row.ingredient_id && Number(row.quantity_g) > 0)
      .map((row) => ({
        ingredient_id: Number(row.ingredient_id),
        quantity_g: Number(row.quantity_g),
      }));
    setSaving(true);
    setError(null);
    try {
      const created = await api.createRecipe({
        name: String(data.get("name") ?? ""),
        description: String(data.get("description") ?? "") || null,
        instructions: String(data.get("instructions") ?? "") || null,
        servings: Number(data.get("servings") || 1),
        created_by: userId,
        ingredients: selected,
      });
      form.reset();
      setRows([{ ingredient_id: "", quantity_g: "100" }]);
      await reload();
      navigate(`/recipes/${created.recipe_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create recipe");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="split">
      <section className="panel">
        <h2>Recipes</h2>
        {recipes.length === 0 ? (
          <p className="empty">No recipes yet. Create one from the catalog on the right.</p>
        ) : (
          <ul className="card-list">
            {recipes.map((recipe) => (
              <li key={recipe.recipe_id}>
                <Link to={`/recipes/${recipe.recipe_id}`}>
                  <strong>{recipe.name}</strong>
                  <span>
                    {recipe.ingredients.length} ingredient
                    {recipe.ingredients.length === 1 ? "" : "s"}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel">
        <h2>New recipe</h2>
        {ingredients.length === 0 ? (
          <p className="empty">
            Add ingredients first on the <Link to="/ingredients">ingredients</Link> page.
          </p>
        ) : (
          <form className="stack" onSubmit={onCreate}>
            <label>
              Name
              <input name="name" required maxLength={255} />
            </label>
            <label>
              Description
              <textarea name="description" rows={2} />
            </label>
            <label>
              Servings this recipe makes
              <input name="servings" type="number" min="0.1" step="0.1" defaultValue="1" />
            </label>
            <fieldset>
              <legend>Ingredients</legend>
              {rows.map((row, index) => (
                <div className="grid-2" key={`${index}-${row.ingredient_id}`}>
                  <select
                    value={row.ingredient_id}
                    onChange={(event) => {
                      const next = [...rows];
                      next[index] = { ...row, ingredient_id: event.target.value };
                      setRows(next);
                    }}
                    required
                  >
                    <option value="">Ingredient</option>
                    {ingredients.map((ingredient) => (
                      <option key={ingredient.ingredient_id} value={ingredient.ingredient_id}>
                        {ingredient.name}
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={row.quantity_g}
                    onChange={(event) => {
                      const next = [...rows];
                      next[index] = { ...row, quantity_g: event.target.value };
                      setRows(next);
                    }}
                    aria-label="Quantity in grams"
                    required
                  />
                </div>
              ))}
              <button
                type="button"
                className="ghost"
                onClick={() => setRows([...rows, { ingredient_id: "", quantity_g: "100" }])}
              >
                Add ingredient
              </button>
            </fieldset>
            <label>
              Instructions
              <textarea name="instructions" rows={3} />
            </label>
            {error ? <p className="error">{error}</p> : null}
            <button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save recipe"}
            </button>
          </form>
        )}
      </section>
    </div>
  );
}
