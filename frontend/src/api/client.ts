import type {
  ChatConfirmResponse,
  ChatMessageResponse,
  DailyProteinSummary,
  Ingredient,
  IngredientCreate,
  MealLog,
  MealLogCreate,
  Recipe,
  RecipeCreate,
  User,
  UserCreate,
  UserUpdate,
} from "./types";

const API = "/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${API}${path}`, { ...init, headers });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      /* ignore non-JSON errors */
    }
    throw new Error(detail);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const api = {
  listUsers: () => request<User[]>("/users"),
  getUser: (userId: number) => request<User>(`/users/${userId}`),
  createUser: (payload: UserCreate) =>
    request<User>("/users", { method: "POST", body: JSON.stringify(payload) }),
  updateUser: (userId: number, payload: UserUpdate) =>
    request<User>(`/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  listIngredients: () => request<Ingredient[]>("/ingredients"),
  createIngredient: (payload: IngredientCreate) =>
    request<Ingredient>("/ingredients", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listRecipes: () => request<Recipe[]>("/recipes"),
  getRecipe: (recipeId: number) => request<Recipe>(`/recipes/${recipeId}`),
  createRecipe: (payload: RecipeCreate) =>
    request<Recipe>("/recipes", { method: "POST", body: JSON.stringify(payload) }),

  listMeals: (userId: number, day: string) =>
    request<MealLog[]>(`/meals?user_id=${userId}&day=${day}`),
  logMeal: (payload: MealLogCreate) =>
    request<MealLog>("/meals", { method: "POST", body: JSON.stringify(payload) }),
  deleteMeal: (mealLogId: number) =>
    request<void>(`/meals/${mealLogId}`, { method: "DELETE" }),

  dailyProtein: (userId: number, day: string) =>
    request<DailyProteinSummary>(`/nutrition/users/${userId}/daily?day=${day}`),

  proposeChatMeal: (payload: {
    user_id: number;
    message: string;
    consumed_at?: string;
    conversation_id?: string;
  }) =>
    request<ChatMessageResponse>("/chat/messages", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  confirmChatMeal: (conversationId: string) =>
    request<ChatConfirmResponse>("/chat/confirm", {
      method: "POST",
      body: JSON.stringify({ conversation_id: conversationId }),
    }),
  cancelChatConversation: (conversationId: string) =>
    request<{ assistant_message: string }>("/chat/cancel", {
      method: "POST",
      body: JSON.stringify({ conversation_id: conversationId }),
    }),
};
