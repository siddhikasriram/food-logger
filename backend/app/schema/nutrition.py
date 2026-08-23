from pydantic import BaseModel, Field


class NutritionTotals(BaseModel):
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    fiber_g: float = 0


class DailyProteinSummary(BaseModel):
    protein_goal_g: float
    protein_consumed_g: float
    protein_remaining_g: float
    progress_percent: float = Field(ge=0)


class ProteinTargetInput(BaseModel):
    weight_kg: float = Field(gt=0)
    protein_factor: float = Field(default=1.4, gt=0)
