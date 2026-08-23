from datetime import datetime

from sqlalchemy.orm import Session

from app.controller.nutrition import NutritionController
from app.model.ingredient import Ingredient
from app.model.meal import MealLog
from app.model.recipe import Recipe, RecipeIngredient
from app.provider.conversation_store import Conversation, ConversationStore
from app.provider.guardrail import Guardrail, InputCategory
from app.provider.meal_parser import MealAssistant
from app.repository.ingredient import IngredientRepository
from app.repository.recipe import RecipeRepository
from app.repository.user import UserRepository
from app.schema.chat import (
    ChatCancelResponse,
    ChatConfirmResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatProposal,
    ChatStatus,
    ParsedIngredient,
)
from app.schema.meal import MealLogRead
from app.schema.nutrition import DailyProteinSummary, NutritionTotals
from app.shared.enums import NutritionSource
from app.shared.exceptions import AppError, NotFoundError, ServiceUnavailableError


YES_RESPONSES = {"yes", "y", "add", "add it", "add recipe", "create", "create it"}
NO_RESPONSES = {"no", "n", "skip", "don't add", "do not add", "no thanks"}


class ChatController:
    def __init__(
        self,
        db: Session,
        guardrail: Guardrail,
        assistant: MealAssistant,
        conversations: ConversationStore,
    ) -> None:
        self.db = db
        self.guardrail = guardrail
        self.assistant = assistant
        self.conversations = conversations
        self.users = UserRepository(db)
        self.ingredients = IngredientRepository(db)
        self.recipes = RecipeRepository(db)

    def message(self, payload: ChatMessageRequest) -> ChatMessageResponse:
        if self.users.get_by_id(payload.user_id) is None:
            raise NotFoundError("User not found")
        if payload.conversation_id is not None:
            return self._continue(payload)
        return self._start(payload)

    def _start(self, payload: ChatMessageRequest) -> ChatMessageResponse:
        classification = self.guardrail.classify(payload.message)
        if classification.category != InputCategory.FOOD:
            category = classification.category.value
            return ChatMessageResponse(
                status=ChatStatus.REJECTED,
                assistant_message=(
                    f"I can only log food right now. That message looks like {category}."
                ),
            )

        extracted = self.assistant.extract_food(payload.message)
        consumed_at = payload.consumed_at or datetime.now()
        recipe = self.recipes.get_by_name(extracted.food_name)
        if recipe is None:
            conversation = self.conversations.create(
                user_id=payload.user_id,
                consumed_at=consumed_at,
                status=ChatStatus.AWAITING_RECIPE_CONSENT,
                extracted_food=extracted,
            )
            return ChatMessageResponse(
                status=conversation.status,
                conversation_id=conversation.conversation_id,
                assistant_message=(
                    f'I could not find a recipe for "{extracted.food_name}". '
                    "Would you like to add it?"
                ),
            )

        proposal = self._existing_recipe_proposal(
            user_id=payload.user_id,
            consumed_at=consumed_at,
            recipe=recipe,
            servings=extracted.servings,
            meal_type=extracted.meal_type,
        )
        conversation = self.conversations.create(
            user_id=payload.user_id,
            consumed_at=consumed_at,
            status=ChatStatus.AWAITING_CONFIRMATION,
            extracted_food=extracted,
            proposal=proposal,
        )
        return self._confirmation_response(conversation)

    def _continue(self, payload: ChatMessageRequest) -> ChatMessageResponse:
        assert payload.conversation_id is not None
        conversation = self.conversations.get(payload.conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found or expired")
        if conversation.user_id != payload.user_id:
            raise NotFoundError("Conversation not found or expired")

        if conversation.status == ChatStatus.AWAITING_RECIPE_CONSENT:
            return self._handle_recipe_consent(conversation, payload.message)
        if conversation.status == ChatStatus.AWAITING_INGREDIENTS:
            return self._handle_ingredients(conversation, payload.message)
        if conversation.status == ChatStatus.AWAITING_CONFIRMATION:
            return self._confirmation_response(conversation)
        raise AppError("This conversation cannot accept another message.")

    def _handle_recipe_consent(
        self, conversation: Conversation, message: str
    ) -> ChatMessageResponse:
        answer = " ".join(message.strip().lower().split())
        if answer in YES_RESPONSES:
            conversation.status = ChatStatus.AWAITING_INGREDIENTS
            self.conversations.put(conversation)
            return ChatMessageResponse(
                status=conversation.status,
                conversation_id=conversation.conversation_id,
                assistant_message=(
                    f"List the ingredients and quantities for "
                    f"{conversation.extracted_food.food_name}."
                ),
            )
        if answer in NO_RESPONSES:
            summary = self._summary_with_unlogged_meal(conversation)
            self.conversations.delete(conversation.conversation_id)
            protein = conversation.extracted_food.protein_grams
            return ChatMessageResponse(
                status=ChatStatus.SUMMARY_ONLY,
                assistant_message=(
                    f"This unlogged meal adds an estimated {protein:.1f}g protein. "
                    f"Your projected total for today is "
                    f"{summary.protein_consumed_g:.1f}g."
                ),
                meal_macros=NutritionTotals(protein_g=protein),
                daily_protein=summary,
                summary_includes_unlogged_meal=True,
            )
        return ChatMessageResponse(
            status=conversation.status,
            conversation_id=conversation.conversation_id,
            assistant_message="Please answer yes or no: would you like to add this recipe?",
        )

    def _handle_ingredients(
        self, conversation: Conversation, message: str
    ) -> ChatMessageResponse:
        extracted = self.assistant.extract_ingredients(
            message, self._ingredient_catalog_context()
        )
        ingredients = self._merge_ingredients(
            self._resolve_proposed_ingredients(extracted.ingredients)
        )
        proposal = ChatProposal(
            user_id=conversation.user_id,
            recipe_id=None,
            recipe_name=conversation.extracted_food.food_name,
            description=(
                f"{conversation.extracted_food.quantity:g} "
                f"{conversation.extracted_food.unit}"
            ),
            servings=conversation.extracted_food.servings,
            meal_type=conversation.extracted_food.meal_type,
            consumed_at=conversation.consumed_at,
            ingredients=ingredients,
            contains_estimates=any(item.is_estimate for item in ingredients),
        )
        conversation.proposal = proposal
        conversation.status = ChatStatus.AWAITING_CONFIRMATION
        self.conversations.put(conversation)
        return self._confirmation_response(conversation)

    def _confirmation_response(
        self, conversation: Conversation
    ) -> ChatMessageResponse:
        if conversation.proposal is None:
            raise AppError("The conversation has no meal ready to confirm.")
        proposal = conversation.proposal
        macros = self._proposal_macros(proposal)
        qualifier = " Estimated nutrition is included." if proposal.contains_estimates else ""
        return ChatMessageResponse(
            status=ChatStatus.AWAITING_CONFIRMATION,
            conversation_id=conversation.conversation_id,
            assistant_message=(
                f"I found {proposal.recipe_name} with {proposal.servings:g} "
                f"serving(s).{qualifier} Confirm to save it to today's log."
            ),
            proposal=proposal,
            meal_macros=macros,
        )

    def confirm(self, conversation_id: str) -> ChatConfirmResponse:
        conversation = self.conversations.take(conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found or expired")
        if (
            conversation.status != ChatStatus.AWAITING_CONFIRMATION
            or conversation.proposal is None
        ):
            self.conversations.put(conversation)
            raise AppError("This conversation is not ready to confirm.")

        proposal = conversation.proposal
        created_recipe = False
        try:
            if self.users.get_by_id(proposal.user_id) is None:
                raise NotFoundError("User not found")
            recipe = self._match_recipe(proposal.recipe_id, proposal.recipe_name)
            if recipe is None:
                recipe_ingredients: list[RecipeIngredient] = []
                for item in self._merge_ingredients(proposal.ingredients):
                    ingredient = self._materialize_ingredient(item)
                    recipe_ingredients.append(
                        RecipeIngredient(
                            ingredient_id=ingredient.ingredient_id,
                            quantity_g=item.quantity_g,
                        )
                    )
                recipe = Recipe(
                    name=proposal.recipe_name.strip(),
                    description=proposal.description,
                    servings=1,
                    created_by=proposal.user_id,
                    recipe_ingredients=recipe_ingredients,
                )
                self.db.add(recipe)
                self.db.flush()
                created_recipe = True

            meal_log = MealLog(
                user_id=proposal.user_id,
                recipe_id=recipe.recipe_id,
                meal_type=proposal.meal_type,
                servings=proposal.servings,
                consumed_at=proposal.consumed_at,
            )
            self.db.add(meal_log)
            self.db.flush()

            nutrition = NutritionController(self.db)
            meal_macros = nutrition.meal_nutrition(recipe.recipe_id, proposal.servings)
            daily = nutrition.daily_protein(
                proposal.user_id, proposal.consumed_at.date()
            )
            contains_estimates = any(
                self.db.get(Ingredient, row.ingredient_id).nutrition_source
                == NutritionSource.LLM_ESTIMATE
                for row in recipe.recipe_ingredients
            )
            self.db.commit()
            self.db.refresh(meal_log)
        except Exception:
            self.db.rollback()
            self.conversations.put(conversation)
            raise

        meal_read = MealLogRead(
            meal_log_id=meal_log.meal_log_id,
            user_id=meal_log.user_id,
            recipe_id=recipe.recipe_id,
            recipe_name=recipe.name,
            meal_type=meal_log.meal_type,
            servings=float(meal_log.servings),
            consumed_at=meal_log.consumed_at,
            created_at=meal_log.created_at,
        )
        return ChatConfirmResponse(
            assistant_message=(
                f"Logged {recipe.name}: {meal_macros.protein_g:.1f}g protein. "
                f"You have {daily.protein_remaining_g:.1f}g remaining today."
            ),
            meal_log=meal_read,
            meal_macros=meal_macros,
            daily_protein=daily,
            created_recipe=created_recipe,
            contains_estimates=contains_estimates,
        )

    def cancel(self, conversation_id: str) -> ChatCancelResponse:
        if not self.conversations.delete(conversation_id):
            raise NotFoundError("Conversation not found or expired")
        return ChatCancelResponse(assistant_message="No changes were saved.")

    def _existing_recipe_proposal(
        self, *, user_id, consumed_at, recipe, servings, meal_type
    ) -> ChatProposal:
        ingredients = [
            self._existing_ingredient(row.ingredient, float(row.quantity_g))
            for row in recipe.recipe_ingredients
        ]
        return ChatProposal(
            user_id=user_id,
            recipe_id=recipe.recipe_id,
            recipe_name=recipe.name,
            description=recipe.description,
            servings=servings,
            meal_type=meal_type,
            consumed_at=consumed_at,
            ingredients=ingredients,
            contains_estimates=any(item.is_estimate for item in ingredients),
        )

    def _summary_with_unlogged_meal(
        self, conversation: Conversation
    ) -> DailyProteinSummary:
        persisted = NutritionController(self.db).daily_protein(
            conversation.user_id, conversation.consumed_at.date()
        )
        consumed = (
            persisted.protein_consumed_g
            + conversation.extracted_food.protein_grams
        )
        goal = persisted.protein_goal_g
        return DailyProteinSummary(
            protein_goal_g=goal,
            protein_consumed_g=consumed,
            protein_remaining_g=max(0.0, goal - consumed),
            progress_percent=(consumed / goal * 100.0) if goal > 0 else 0.0,
        )

    def _ingredient_catalog_context(self) -> dict[str, object]:
        return {
            "ingredients": [
                {
                    "id": item.ingredient_id,
                    "name": item.name,
                    "calories_per_100g": float(item.calories_per_100g),
                    "protein_per_100g": float(item.protein_per_100g),
                    "carbs_per_100g": float(item.carbs_per_100g),
                    "fat_per_100g": float(item.fat_per_100g),
                    "fiber_per_100g": float(item.fiber_per_100g),
                }
                for item in self.ingredients.list_all()
            ]
        }

    def _match_recipe(self, recipe_id: int | None, name: str) -> Recipe | None:
        if recipe_id is not None:
            recipe = self.recipes.get_by_id(recipe_id)
            if recipe is None:
                raise ServiceUnavailableError(
                    "The selected catalog recipe is no longer available."
                )
            return recipe
        return self.recipes.get_by_name(name)

    def _resolve_proposed_ingredients(
        self, parsed: list[ParsedIngredient]
    ) -> list[ParsedIngredient]:
        resolved: list[ParsedIngredient] = []
        for item in parsed:
            ingredient = None
            if item.ingredient_id is not None:
                ingredient = self.ingredients.get_by_id(item.ingredient_id)
                if ingredient is None:
                    raise ServiceUnavailableError(
                        "A selected catalog ingredient is no longer available."
                    )
            else:
                ingredient = self.ingredients.get_by_name(item.name)
            resolved.append(
                self._existing_ingredient(ingredient, item.quantity_g)
                if ingredient is not None
                else item
            )
        return resolved

    def _existing_ingredient(
        self, ingredient: Ingredient, quantity_g: float
    ) -> ParsedIngredient:
        return ParsedIngredient(
            ingredient_id=ingredient.ingredient_id,
            name=ingredient.name,
            quantity_g=quantity_g,
            calories_per_100g=float(ingredient.calories_per_100g),
            protein_per_100g=float(ingredient.protein_per_100g),
            carbs_per_100g=float(ingredient.carbs_per_100g),
            fat_per_100g=float(ingredient.fat_per_100g),
            fiber_per_100g=float(ingredient.fiber_per_100g),
            is_estimate=ingredient.nutrition_source == NutritionSource.LLM_ESTIMATE,
        )

    def _merge_ingredients(
        self, ingredients: list[ParsedIngredient]
    ) -> list[ParsedIngredient]:
        merged: dict[str, ParsedIngredient] = {}
        for item in ingredients:
            key = (
                f"id:{item.ingredient_id}"
                if item.ingredient_id is not None
                else f"name:{item.name.strip().lower()}"
            )
            if key in merged:
                current = merged[key]
                merged[key] = current.model_copy(
                    update={"quantity_g": current.quantity_g + item.quantity_g}
                )
            else:
                merged[key] = item
        return list(merged.values())

    def _materialize_ingredient(self, item: ParsedIngredient) -> Ingredient:
        ingredient = (
            self.ingredients.get_by_id(item.ingredient_id)
            if item.ingredient_id is not None
            else self.ingredients.get_by_name(item.name)
        )
        if item.ingredient_id is not None and ingredient is None:
            raise ServiceUnavailableError(
                "A selected catalog ingredient is no longer available."
            )
        if ingredient is not None:
            return ingredient

        ingredient = Ingredient(
            name=item.name.strip(),
            calories_per_100g=item.calories_per_100g,
            protein_per_100g=item.protein_per_100g,
            carbs_per_100g=item.carbs_per_100g,
            fat_per_100g=item.fat_per_100g,
            fiber_per_100g=item.fiber_per_100g,
            nutrition_source=NutritionSource.LLM_ESTIMATE,
        )
        self.db.add(ingredient)
        self.db.flush()
        return ingredient

    def _proposal_macros(self, proposal: ChatProposal) -> NutritionTotals:
        if proposal.recipe_id is not None:
            return NutritionController(self.db).meal_nutrition(
                proposal.recipe_id, proposal.servings
            )

        totals = NutritionTotals()
        for item in proposal.ingredients:
            factor = item.quantity_g / 100
            totals = NutritionTotals(
                calories=totals.calories + float(item.calories_per_100g or 0) * factor,
                protein_g=totals.protein_g + float(item.protein_per_100g or 0) * factor,
                carbs_g=totals.carbs_g + float(item.carbs_per_100g or 0) * factor,
                fat_g=totals.fat_g + float(item.fat_per_100g or 0) * factor,
                fiber_g=totals.fiber_g + float(item.fiber_per_100g or 0) * factor,
            )
        return NutritionTotals(
            calories=totals.calories * proposal.servings,
            protein_g=totals.protein_g * proposal.servings,
            carbs_g=totals.carbs_g * proposal.servings,
            fat_g=totals.fat_g * proposal.servings,
            fiber_g=totals.fiber_g * proposal.servings,
        )
