import { FormEvent, useEffect, useState } from "react";

import { api } from "../api/client";
import type { Ingredient } from "../api/types";

export function IngredientsPage() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function reload() {
    setIngredients(await api.listIngredients());
  }

  useEffect(() => {
    void reload().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "Could not load ingredients");
    });
  }, []);

  async function onCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setSaving(true);
    setError(null);
    try {
      await api.createIngredient({
        name: String(data.get("name") ?? ""),
        calories_per_100g: Number(data.get("calories_per_100g")),
        protein_per_100g: Number(data.get("protein_per_100g")),
        carbs_per_100g: Number(data.get("carbs_per_100g")),
        fat_per_100g: Number(data.get("fat_per_100g")),
        fiber_per_100g: Number(data.get("fiber_per_100g") || 0),
      });
      form.reset();
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create ingredient");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="split">
      <section className="panel">
        <h2>Catalog</h2>
        {ingredients.length === 0 ? (
          <p className="empty">No ingredients yet. Add macros per 100g on the right.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>kcal</th>
                <th>P</th>
                <th>C</th>
                <th>F</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {ingredients.map((ingredient) => (
                <tr key={ingredient.ingredient_id}>
                  <td>{ingredient.name}</td>
                  <td>{ingredient.calories_per_100g}</td>
                  <td>{ingredient.protein_per_100g}</td>
                  <td>{ingredient.carbs_per_100g}</td>
                  <td>{ingredient.fat_per_100g}</td>
                  <td>
                    {ingredient.nutrition_source === "llm_estimate" ? (
                      <span className="estimate-badge">AI estimate</span>
                    ) : (
                      "Manual"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="panel">
        <h2>Add ingredient</h2>
        <p className="lede">Values are per 100g.</p>
        <form className="stack" onSubmit={onCreate}>
          <label>
            Name
            <input name="name" required maxLength={255} />
          </label>
          <div className="grid-2">
            <label>
              Calories
              <input name="calories_per_100g" type="number" min="0" step="0.1" required />
            </label>
            <label>
              Protein (g)
              <input name="protein_per_100g" type="number" min="0" step="0.1" required />
            </label>
            <label>
              Carbs (g)
              <input name="carbs_per_100g" type="number" min="0" step="0.1" required />
            </label>
            <label>
              Fat (g)
              <input name="fat_per_100g" type="number" min="0" step="0.1" required />
            </label>
          </div>
          <label>
            Fiber (g)
            <input name="fiber_per_100g" type="number" min="0" step="0.1" defaultValue="0" />
          </label>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit" disabled={saving}>
            {saving ? "Saving…" : "Add to catalog"}
          </button>
        </form>
      </section>
    </div>
  );
}
