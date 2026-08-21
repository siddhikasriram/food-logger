import { FormEvent, useState } from "react";

import { api } from "../api/client";
import type {
  ChatConfirmResponse,
  ChatMessageResponse,
  NutritionTotals,
} from "../api/types";
import { useUser } from "../context/UserContext";
import { localDateTime } from "../lib/datetime";

type ChatEntry = {
  id: number;
  role: "user" | "assistant";
  text: string;
  result?: ChatConfirmResponse;
};

function MacroLine({ macros }: { macros: NutritionTotals }) {
  return (
    <p className="macro-line">
      <strong>{macros.protein_g.toFixed(1)}g protein</strong>
      <span>{macros.calories.toFixed(0)} kcal</span>
      <span>{macros.carbs_g.toFixed(1)}g carbs</span>
      <span>{macros.fat_g.toFixed(1)}g fat</span>
    </p>
  );
}

export function ChatPage() {
  const { userId } = useUser();
  const [text, setText] = useState("");
  const [entries, setEntries] = useState<ChatEntry[]>([
    {
      id: 0,
      role: "assistant",
      text: "Tell me what you ate. I’ll check your recipe catalog and prepare it for confirmation.",
    },
  ]);
  const [pending, setPending] = useState<ChatMessageResponse | null>(null);
  const [loading, setLoading] = useState(false);

  function addEntry(entry: Omit<ChatEntry, "id">) {
    setEntries((current) => [...current, { ...entry, id: Date.now() + current.length }]);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = text.trim();
    if (!message || !userId || pending) {
      return;
    }
    addEntry({ role: "user", text: message });
    setText("");
    setLoading(true);
    try {
      const response = await api.proposeChatMeal({
        user_id: userId,
        message,
        consumed_at: localDateTime(),
      });
      addEntry({ role: "assistant", text: response.assistant_message });
      setPending(response);
    } catch (error) {
      addEntry({
        role: "assistant",
        text: error instanceof Error ? error.message : "I could not parse that meal.",
      });
    } finally {
      setLoading(false);
    }
  }

  async function confirm() {
    if (!pending) {
      return;
    }
    setLoading(true);
    try {
      const result = await api.confirmChatMeal(pending.proposal);
      addEntry({ role: "assistant", text: result.assistant_message, result });
      setPending(null);
    } catch (error) {
      addEntry({
        role: "assistant",
        text: error instanceof Error ? error.message : "I could not log that meal.",
      });
    } finally {
      setLoading(false);
    }
  }

  function cancel() {
    setPending(null);
    addEntry({ role: "assistant", text: "No changes were saved." });
  }

  return (
    <section className="chat-panel">
      <div className="chat-heading">
        <div>
          <p className="eyebrow">Meal assistant</p>
          <h2>Log food naturally</h2>
        </div>
        <p className="muted">New nutrition values are AI estimates and require confirmation.</p>
      </div>

      <div className="chat-thread" aria-live="polite">
        {entries.map((entry) => (
          <div key={entry.id} className={`chat-row ${entry.role}`}>
            <div className="chat-bubble">
              <p>{entry.text}</p>
              {entry.result ? (
                <div className="chat-result">
                  <MacroLine macros={entry.result.meal_macros} />
                  <p>
                    Today: {entry.result.daily_protein.protein_consumed_g.toFixed(1)}g of{" "}
                    {entry.result.daily_protein.protein_goal_g.toFixed(1)}g protein
                  </p>
                </div>
              ) : null}
            </div>
          </div>
        ))}
        {loading ? (
          <div className="chat-row assistant">
            <div className="chat-bubble typing">Checking your food catalog…</div>
          </div>
        ) : null}
      </div>

      {pending ? (
        <article className="confirmation-card">
          <div className="confirmation-title">
            <div>
              <p className="eyebrow">
                {pending.proposal.recipe_id ? "Catalog match" : "New recipe"}
              </p>
              <h3>{pending.proposal.recipe_name}</h3>
            </div>
            {pending.proposal.contains_estimates ? (
              <span className="estimate-badge">AI estimate</span>
            ) : null}
          </div>
          <p>
            {pending.proposal.meal_type} · {pending.proposal.servings} serving(s)
          </p>
          <ul className="plain-list confirmation-ingredients">
            {pending.proposal.ingredients.map((ingredient, index) => (
              <li key={`${ingredient.ingredient_id ?? ingredient.name}-${index}`}>
                {ingredient.quantity_g}g {ingredient.name}
                {ingredient.is_estimate ? (
                  <span className="estimate-label"> estimated</span>
                ) : null}
              </li>
            ))}
          </ul>
          <MacroLine macros={pending.meal_macros} />
          <div className="confirmation-actions">
            <button type="button" onClick={() => void confirm()} disabled={loading}>
              Confirm and log
            </button>
            <button type="button" className="ghost" onClick={cancel} disabled={loading}>
              Cancel
            </button>
          </div>
        </article>
      ) : null}

      <form className="chat-compose" onSubmit={onSubmit}>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Example: I ate two servings of chicken curry for lunch"
          rows={2}
          maxLength={2000}
          disabled={loading || pending !== null}
          aria-label="Describe your meal"
        />
        <button type="submit" disabled={loading || pending !== null || !text.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}
