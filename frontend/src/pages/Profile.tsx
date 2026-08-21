import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";
import type { User } from "../api/types";
import { useUser } from "../context/UserContext";

function optionalNumber(value: string): number | undefined {
  if (!value.trim()) {
    return undefined;
  }
  return Number(value);
}

export function ProfilePage() {
  const { user, userId, setCurrentUserId, refresh } = useUser();
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void api.listUsers().then(setUsers);
  }, [user]);

  async function onSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!userId) {
      return;
    }
    const data = new FormData(event.currentTarget);
    setSaving(true);
    setError(null);
    try {
      await api.updateUser(userId, {
        name: String(data.get("name") ?? ""),
        weight_kg: optionalNumber(String(data.get("weight_kg") ?? "")),
        protein_goal_g: optionalNumber(String(data.get("protein_goal_g") ?? "")),
        calorie_goal: optionalNumber(String(data.get("calorie_goal") ?? "")),
      });
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update profile");
    } finally {
      setSaving(false);
    }
  }

  if (!user) {
    return <p>Loading profile…</p>;
  }

  return (
    <div className="split">
      <section className="panel">
        <h2>Your goals</h2>
        <form className="stack" onSubmit={onSave}>
          <label>
            Name
            <input name="name" defaultValue={user.name} required />
          </label>
          <p className="muted">{user.email}</p>
          <div className="grid-2">
            <label>
              Weight (kg)
              <input
                name="weight_kg"
                type="number"
                min="1"
                step="0.1"
                defaultValue={user.weight_kg ?? ""}
              />
            </label>
            <label>
              Protein goal (g)
              <input
                name="protein_goal_g"
                type="number"
                min="0"
                step="0.1"
                defaultValue={user.protein_goal_g ?? ""}
              />
            </label>
          </div>
          <label>
            Calorie goal
            <input
              name="calorie_goal"
              type="number"
              min="0"
              step="1"
              defaultValue={user.calorie_goal ?? ""}
            />
          </label>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save profile"}
          </button>
        </form>
      </section>

      <section className="panel">
        <h2>Switch profile</h2>
        <ul className="card-list">
          {users.map((item) => (
            <li key={item.user_id}>
              <button
                type="button"
                className={item.user_id === userId ? "user-chip current" : "user-chip"}
                onClick={() => setCurrentUserId(item.user_id)}
              >
                <strong>{item.name}</strong>
                <span>{item.email}</span>
              </button>
            </li>
          ))}
        </ul>
        <p className="lede">
          Need another person on this device? <Link to="/setup?new=1">Create a profile</Link>.
        </p>
      </section>
    </div>
  );
}
