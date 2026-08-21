export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export type User = {
  user_id: number;
  name: string;
  email: string;
  height_cm: number | null;
  weight_kg: number | null;
  protein_goal_g: number | null;
  calorie_goal: number | null;
  created_at: string;
  updated_at: string;
};

export type UserCreate = {
  name: string;
  email: string;
  height_cm?: number | null;
  weight_kg?: number | null;
  protein_goal_g?: number | null;
  calorie_goal?: number | null;
};

export type UserUpdate = {
  name?: string;
  height_cm?: number | null;
  weight_kg?: number | null;
  protein_goal_g?: number | null;
  calorie_goal?: number | null;
};

export type Ingredient = {
  ingredient_id: number;
  name: string;
  calories_per_100g: number;
  protein_per_100g: number;
  carbs_per_100g: number;
  fat_per_100g: number;
  fiber_per_100g: number;
  nutrition_source: "manual" | "llm_estimate";
  created_at: string;
  updated_at: string;
};

export type IngredientCreate = {
  name: string;
  calories_per_100g: number;
  protein_per_100g: number;
  carbs_per_100g: number;
  fat_per_100g: number;
  fiber_per_100g?: number;
};

export type RecipeIngredientDetail = {
  ingredient_id: number;
  name: string;
  quantity_g: number;
};

export type RecipeTag = {
  tag_id: number;
  name: string;
};

export type Recipe = {
  recipe_id: number;
  name: string;
  description: string | null;
  instructions: string | null;
  servings: number;
  created_by: number | null;
  created_at: string;
  updated_at: string;
  ingredients: RecipeIngredientDetail[];
  tags: RecipeTag[];
};

export type RecipeCreate = {
  name: string;
  description?: string | null;
  instructions?: string | null;
  servings?: number;
  created_by?: number | null;
  ingredients: { ingredient_id: number; quantity_g: number }[];
};

export type MealLog = {
  meal_log_id: number;
  user_id: number;
  recipe_id: number;
  recipe_name: string;
  meal_type: MealType;
  servings: number;
  consumed_at: string;
  created_at: string;
};

export type MealLogCreate = {
  user_id: number;
  recipe_id: number;
  meal_type: MealType;
  servings: number;
  consumed_at: string;
};

export type DailyProteinSummary = {
  protein_goal_g: number;
  protein_consumed_g: number;
  protein_remaining_g: number;
  progress_percent: number;
};

export type NutritionTotals = {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
};

export type ParsedIngredient = {
  ingredient_id: number | null;
  name: string;
  quantity_g: number;
  calories_per_100g: number | null;
  protein_per_100g: number | null;
  carbs_per_100g: number | null;
  fat_per_100g: number | null;
  fiber_per_100g: number | null;
  is_estimate: boolean;
};

export type ChatProposal = {
  user_id: number;
  recipe_id: number | null;
  recipe_name: string;
  description: string | null;
  servings: number;
  meal_type: MealType;
  consumed_at: string;
  ingredients: ParsedIngredient[];
  contains_estimates: boolean;
};

export type ChatMessageResponse = {
  assistant_message: string;
  needs_confirmation: boolean;
  proposal: ChatProposal;
  meal_macros: NutritionTotals;
};

export type ChatConfirmResponse = {
  assistant_message: string;
  meal_log: MealLog;
  meal_macros: NutritionTotals;
  daily_protein: DailyProteinSummary;
  created_recipe: boolean;
  contains_estimates: boolean;
};
