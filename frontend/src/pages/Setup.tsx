import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";

import { api } from "../api/client";
import { useUser } from "../context/UserContext";

function optionalNumber(value: string): number | undefined {
  if (!value.trim()) {
    return undefined;
  }
  return Number(value);
}

export function SetupPage() {
  const { userId, setCurrentUserId } = useUser();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const allowNew = searchParams.get("new") === "1";
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  if (userId && !allowNew) {
    return <Navigate to="/" replace />;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSaving(true);
    setError(null);
    try {
      const created = await api.createUser({
        name: String(form.get("name") ?? ""),
        email: String(form.get("email") ?? ""),
        weight_kg: optionalNumber(String(form.get("weight_kg") ?? "")),
        protein_goal_g: optionalNumber(String(form.get("protein_goal_g") ?? "")),
        calorie_goal: optionalNumber(String(form.get("calorie_goal") ?? "")),
      });
      setCurrentUserId(created.user_id);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create profile");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="narrow-card">
      <p className="eyebrow">Get started</p>
      <h2>Create your profile</h2>
      <p className="lede">
        Protein goal is optional — if you skip it and enter weight, we set it to 1.4g per kg.
      </p>
      <form className="stack" onSubmit={onSubmit}>
        <label>
          Name
          <input name="name" required maxLength={255} autoComplete="name" />
        </label>
        <label>
          Email
          <input name="email" type="email" required autoComplete="email" />
        </label>
        <div className="grid-2">
          <label>
            Weight (kg)
            <input name="weight_kg" type="number" min="1" step="0.1" />
          </label>
          <label>
            Protein goal (g)
            <input name="protein_goal_g" type="number" min="0" step="0.1" />
          </label>
        </div>
        <label>
          Calorie goal
          <input name="calorie_goal" type="number" min="0" step="1" />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Start logging"}
        </button>
        {userId ? (
          <p className="muted">
            <Link to="/profile">Cancel and go back</Link>
          </p>
        ) : null}
      </form>
    </section>
  );
}
