import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";
import type { DailyProteinSummary, MealLog, MealType, Recipe } from "../api/types";
import { useUser } from "../context/UserContext";
import { localDate, localDateTime } from "../lib/datetime";

const MEAL_TYPES: MealType[] = ["breakfast", "lunch", "dinner", "snack"];

export function TodayPage() {
  const { userId } = useUser();
  const day = localDate();
  const [summary, setSummary] = useState<DailyProteinSummary | null>(null);
  const [meals, setMeals] = useState<MealLog[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function reload() {
    if (!userId) {
      return;
    }
    const [nextSummary, nextMeals, nextRecipes] = await Promise.all([
      api.dailyProtein(userId, day),
      api.listMeals(userId, day),
      api.listRecipes(),
    ]);
    setSummary(nextSummary);
    setMeals(nextMeals);
    setRecipes(nextRecipes);
  }

  useEffect(() => {
    void reload().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "Could not load today");
    });
  }, [userId, day]);

  async function onLog(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!userId) {
      return;
    }
    const form = event.currentTarget;
    const data = new FormData(form);
    setSaving(true);
    setError(null);
    try {
      await api.logMeal({
        user_id: userId,
        recipe_id: Number(data.get("recipe_id")),
        meal_type: String(data.get("meal_type")) as MealType,
        servings: Number(data.get("servings")),
        consumed_at: localDateTime(),
      });
      form.reset();
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not log meal");
    } finally {
      setSaving(false);
    }
  }

  async function undo(mealLogId: number) {
    await api.deleteMeal(mealLogId);
    await reload();
  }

  const progress = Math.min(summary?.progress_percent ?? 0, 100);

  return (
    <div className="split">
      <section className="panel protein-panel">
        <p className="eyebrow">Today · {day}</p>
        <h2>Protein</h2>
        {summary ? (
          <>
            <div className="progress" aria-label="Protein progress">
              <span style={{ width: `${progress}%` }} />
            </div>
            <dl className="stats">
              <div>
                <dt>Eaten</dt>
                <dd>{summary.protein_consumed_g.toFixed(0)} g</dd>
              </div>
              <div>
                <dt>Goal</dt>
                <dd>{summary.protein_goal_g.toFixed(0)} g</dd>
              </div>
              <div>
                <dt>Left</dt>
                <dd>{summary.protein_remaining_g.toFixed(0)} g</dd>
              </div>
            </dl>
          </>
        ) : (
          <p>Loading protein…</p>
        )}
      </section>

      <section className="panel">
        <h2>Log a meal</h2>
        {recipes.length === 0 ? (
          <p className="empty">
            No recipes yet. <Link to="/recipes">Create a recipe</Link> after adding ingredients.
          </p>
        ) : (
          <form className="stack" onSubmit={onLog}>
            <label>
              Recipe
              <select name="recipe_id" required defaultValue="">
                <option value="" disabled>
                  Choose a recipe
                </option>
                {recipes.map((recipe) => (
                  <option key={recipe.recipe_id} value={recipe.recipe_id}>
                    {recipe.name}
                  </option>
                ))}
              </select>
            </label>
            <div className="grid-2">
              <label>
                Meal
                <select name="meal_type" defaultValue="lunch">
                  {MEAL_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Servings
                <input name="servings" type="number" min="0.1" step="0.1" defaultValue="1" required />
              </label>
            </div>
            <button type="submit" disabled={saving}>
              {saving ? "Logging…" : "Add to today"}
            </button>
          </form>
        )}
        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="panel span-2">
        <h2>Meals</h2>
        {meals.length === 0 ? (
          <p className="empty">Nothing logged yet. Add a meal above.</p>
        ) : (
          <ul className="meal-list">
            {meals.map((meal) => (
              <li key={meal.meal_log_id}>
                <div>
                  <strong>{meal.recipe_name}</strong>
                  <span>
                    {meal.meal_type} · {meal.servings} serving
                    {meal.servings === 1 ? "" : "s"}
                  </span>
                </div>
                <button type="button" className="ghost" onClick={() => void undo(meal.meal_log_id)}>
                  Undo
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
