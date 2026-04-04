# schemas/dashboard.py

from pydantic import BaseModel
from typing import List


class MonthlySale(BaseModel):
    month: int  # ← must be int, not str
    total_sales: int
    revenue: float


class DashboardResponse(BaseModel):
    total_inventories: int
    available_inventories: int
    sold_inventories: int
    total_customers: int
    total_sales: int
    total_revenue: float
    pending_test_drives: int
    monthly_sales: list[MonthlySale]
