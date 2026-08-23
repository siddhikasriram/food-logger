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
  preview?: ChatMessageResponse;
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
      text: "Tell me what you ate. I’ll check your recipe catalog before anything is saved.",
    },
  ]);
  const [pending, setPending] = useState<ChatMessageResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const awaitingConfirmation = pending?.status === "awaiting_confirmation";

  function addEntry(entry: Omit<ChatEntry, "id">) {
    setEntries((current) => [...current, { ...entry, id: Date.now() + current.length }]);
  }

  function acceptResponse(response: ChatMessageResponse) {
    addEntry({
      role: "assistant",
      text: response.assistant_message,
      preview: response.status === "summary_only" ? response : undefined,
    });
    if (
      response.status === "awaiting_recipe_consent" ||
      response.status === "awaiting_ingredients" ||
      response.status === "awaiting_confirmation"
    ) {
      setPending(response);
    } else {
      setPending(null);
    }
  }

  async function sendMessage(message: string) {
    if (!userId || awaitingConfirmation) {
      return;
    }
    addEntry({ role: "user", text: message });
    setLoading(true);
    try {
      const response = await api.proposeChatMeal({
        user_id: userId,
        message,
        consumed_at: pending ? undefined : localDateTime(),
        conversation_id: pending?.conversation_id ?? undefined,
      });
      acceptResponse(response);
    } catch (error) {
      addEntry({
        role: "assistant",
        text: error instanceof Error ? error.message : "I could not process that message.",
      });
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = text.trim();
    if (!message || loading || awaitingConfirmation) {
      return;
    }
    setText("");
    await sendMessage(message);
  }

  async function answerRecipeConsent(answer: "yes" | "no") {
    if (loading) {
      return;
    }
    await sendMessage(answer);
  }

  async function confirm() {
    const conversationId = pending?.conversation_id;
    if (!conversationId || !awaitingConfirmation) {
      return;
    }
    setLoading(true);
    try {
      const result = await api.confirmChatMeal(conversationId);
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

  async function cancel() {
    const conversationId = pending?.conversation_id;
    if (!conversationId) {
      return;
    }
    setLoading(true);
    try {
      const response = await api.cancelChatConversation(conversationId);
      addEntry({ role: "assistant", text: response.assistant_message });
      setPending(null);
    } catch (error) {
      addEntry({
        role: "assistant",
        text: error instanceof Error ? error.message : "I could not cancel that conversation.",
      });
    } finally {
      setLoading(false);
    }
  }

  const proposal = awaitingConfirmation ? pending?.proposal : null;
  const proposalMacros = awaitingConfirmation ? pending?.meal_macros : null;
  const inputPlaceholder =
    pending?.status === "awaiting_ingredients"
      ? "Example: 200g chicken, 100g pasta, 50g tomato sauce"
      : "Example: I ate two servings of chicken curry for lunch";

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
              {entry.preview?.meal_macros && entry.preview.daily_protein ? (
                <div className="chat-result">
                  <MacroLine macros={entry.preview.meal_macros} />
                  <p>
                    Projected today:{" "}
                    {entry.preview.daily_protein.protein_consumed_g.toFixed(1)}g of{" "}
                    {entry.preview.daily_protein.protein_goal_g.toFixed(1)}g protein
                    {entry.preview.summary_includes_unlogged_meal ? " (meal not saved)" : ""}
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

      {pending?.status === "awaiting_recipe_consent" ? (
        <div className="confirmation-actions">
          <button type="button" onClick={() => void answerRecipeConsent("yes")} disabled={loading}>
            Add recipe
          </button>
          <button
            type="button"
            className="ghost"
            onClick={() => void answerRecipeConsent("no")}
            disabled={loading}
          >
            Don’t add
          </button>
          <button type="button" className="ghost" onClick={() => void cancel()} disabled={loading}>
            Cancel
          </button>
        </div>
      ) : null}

      {pending?.status === "awaiting_ingredients" ? (
        <div className="confirmation-actions">
          <button type="button" className="ghost" onClick={() => void cancel()} disabled={loading}>
            Cancel recipe
          </button>
        </div>
      ) : null}

      {proposal && proposalMacros ? (
        <article className="confirmation-card">
          <div className="confirmation-title">
            <div>
              <p className="eyebrow">{proposal.recipe_id ? "Catalog match" : "New recipe"}</p>
              <h3>{proposal.recipe_name}</h3>
            </div>
            {proposal.contains_estimates ? (
              <span className="estimate-badge">AI estimate</span>
            ) : null}
          </div>
          <p>
            {proposal.meal_type} · {proposal.servings} serving(s)
          </p>
          <ul className="plain-list confirmation-ingredients">
            {proposal.ingredients.map((ingredient, index) => (
              <li key={`${ingredient.ingredient_id ?? ingredient.name}-${index}`}>
                {ingredient.quantity_g}g {ingredient.name}
                {ingredient.is_estimate ? (
                  <span className="estimate-label"> estimated</span>
                ) : null}
              </li>
            ))}
          </ul>
          <MacroLine macros={proposalMacros} />
          <div className="confirmation-actions">
            <button type="button" onClick={() => void confirm()} disabled={loading}>
              Confirm and log
            </button>
            <button type="button" className="ghost" onClick={() => void cancel()} disabled={loading}>
              Cancel
            </button>
          </div>
        </article>
      ) : null}

      <form className="chat-compose" onSubmit={(event) => void onSubmit(event)}>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder={inputPlaceholder}
          rows={2}
          maxLength={2000}
          disabled={loading || awaitingConfirmation}
          aria-label="Describe your meal"
        />
        <button type="submit" disabled={loading || awaitingConfirmation || !text.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}
