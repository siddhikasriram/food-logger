from pydantic import BaseModel, Field

from app.shared.enums import QuantityUnit


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total: int


class Quantity(BaseModel):
    """Quantity in grams for the MVP. Unit is explicit so other units can be added later."""

    amount: float = Field(gt=0)
    unit: QuantityUnit = QuantityUnit.GRAMS

    @property
    def grams(self) -> float:
        if self.unit == QuantityUnit.GRAMS:
            return self.amount
        raise NotImplementedError(f"Conversion from {self.unit} is not implemented")
