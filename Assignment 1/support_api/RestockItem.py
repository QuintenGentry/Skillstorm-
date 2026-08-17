

from typing import Literal
from pydantic import Field, BaseModel

"""
- `sku: str`
- `warehouse: str`
- `quantity: int` — must be greater than 0 (reject zero and negative values)
- `unit_cost: float` — must be greater than 0
- `category: Literal["electronics", "perishable", "apparel", "hardware"]`
"""

Category = Literal["electronics", "perishable", "apparel", "hardware"]

# Pydantic file, allowing restrictions on variables.
class RestockItem(BaseModel):
    sku: str
    warehouse: str
    quantity: int = Field(gt = 0)
    unit_cost: float = Field(gt = 0)
    category: Category





