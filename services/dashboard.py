from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from functools import lru_cache
from models import Inventory, Sale, Customer, TestDrive


# pseudo
@lru_cache(maxsize=1)  # Cache the dashboard data for 5 minutes to reduce DB load
def get_dashboard_data(db: Session):

    # --- Inventorys aggregation (single query)
    Inventory_stats = db.query(
        func.count(Inventory.id).label("total"),
        func.sum(case((Inventory.status == "available", 1), else_=0)).label(
            "available"
        ),
        func.sum(case((Inventory.status == "sold", 1), else_=0)).label("sold"),
    ).one()

    # --- Sales aggregation (single query)
    sale_stats = db.query(
        func.count(Sale.id).label("total_sales"),
        func.coalesce(func.sum(Sale.sale_price), 0).label("total_revenue"),
    ).one()

    # --- Customer count
    total_customers = db.query(func.count(Customer.id)).scalar()

    # --- Pending test drives
    pending_test_drives = (
        db.query(func.count(TestDrive.id))
        .filter(TestDrive.status == "pending")
        .scalar()
    )

    # --- Monthly sales (already optimized enough)
    monthly_data = (
        db.query(
            extract("month", Sale.created_at).label("month"),
            func.count(Sale.id).label("total_sales"),
            func.sum(Sale.sale_price).label("revenue"),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    monthly_sales = [
        {
            "month": int(data.month),
            "total_sales": data.total_sales,
            "revenue": float(data.revenue or 0),
        }
        for data in monthly_data
    ]

    return {
        "total_inventories": Inventory_stats.total or 0,
        "available_inventories": Inventory_stats.available or 0,
        "sold_inventories": Inventory_stats.sold or 0,
        "total_customers": total_customers,
        "total_sales": sale_stats.total_sales or 0,
        "total_revenue": float(sale_stats.total_revenue or 0),
        "pending_test_drives": pending_test_drives,
        "monthly_sales": monthly_sales,
    }
