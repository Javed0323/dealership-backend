# services/query_utils.py

from operator import or_

from sqlalchemy import String, String, or_
from sqlalchemy.orm import Query, joinedload
from sqlalchemy.sql import func
from sqlalchemy.types import Boolean, Integer, Float

from models.car import Car
from fastapi import HTTPException
from typing import Any


# ── Type coercion ─────────────────────────────────────────────────────────────


def _coerce(column, value: str) -> Any:
    try:
        col_type = column.property.columns[0].type
        if isinstance(col_type, Boolean):
            return value.lower() in ("true", "1", "yes")
        if isinstance(col_type, Integer):
            return int(value)
        if isinstance(col_type, Float):
            return float(value)
    except Exception:
        pass
    return value


# ── Field resolver ────────────────────────────────────────────────────────────


def _resolve_column(field: str, primary_model, related_models: dict):
    """
    Returns (column_attr, model) for a given field name.
    Checks primary model first, then related models.
    """
    if hasattr(primary_model, field):
        return getattr(primary_model, field), primary_model

    for model in related_models.values():
        if hasattr(model, field):
            return getattr(model, field), model

    return None, None


# ── Core utils ────────────────────────────────────────────────────────────────


def apply_search(query: Query, search: str, primary_model, related_models: dict = {}, joined: set = None) -> Query: #type: ignore
    if joined is None:
        joined = set()
    if not search or not search.strip():
        return query

    term = f"%{search.strip()}%"

    # Join Car if not already joined (assuming primary is Inventory)
    if Car not in joined and primary_model != Car:
        query = query.join(Car)
        joined.add(Car)

    query = query.filter(
        or_(
            Car.make.ilike(term),
            Car.model.ilike(term),
            Car.year.cast(String).ilike(term),
            Car.category.ilike(term),
            Car.engine.has(Car.engine.property.mapper.class_.fuel_type.ilike(term)),
        )
    )
    return query



def apply_filters(
    query: Query,
    primary_model,
    filters: dict,
    related_models: dict = {},  # e.g. {"engine": CarEngine, "dimensions": CarDimensions}
    joined: set = None,  # tracks which models are already joined (mutated in place) # type: ignore
) -> Query:
    if joined is None:
        joined = set()

    for raw_field, value in filters.items():
        if value is None or value == "":
            continue

        field, operator = (
            raw_field.split("__", 1) if "__" in raw_field else (raw_field, "eq")
        )

        column, owner_model = _resolve_column(field, primary_model, related_models)

        if column is None:
            continue  # unknown field — silently skip

        # Join related model if not already joined
        if owner_model is not primary_model and owner_model not in joined:
            query = query.join(owner_model)  # type: ignore
            joined.add(owner_model)

        # Type coercion
        if operator not in ("in", "isnull"):
            value = _coerce(column, value)

        # Apply operator
        if operator == "eq":
            query = query.filter(column == value)

        elif operator == "neq":
            query = query.filter(column != value)

        elif operator == "gt":
            query = query.filter(column > value)

        elif operator == "gte":
            query = query.filter(column >= value)

        elif operator == "lt":
            query = query.filter(column < value)

        elif operator == "lte":
            query = query.filter(column <= value)

        elif operator == "like":
            query = query.filter(column.ilike(f"%{value}%"))

        elif operator == "in":
            items = value.split(",") if isinstance(value, str) else value
            # Coerce each item individually
            items = [_coerce(column, v.strip()) for v in items]
            query = query.filter(column.in_(items))

        elif operator == "isnull":
            is_null = value.lower() in ("true", "1")
            query = query.filter(column.is_(None) if is_null else column.isnot(None))

    return query


def apply_sorting(
    query: Query,
    primary_model,
    sort: str,
    related_models: dict = {},
    joined: set = None,  # type: ignore
) -> Query:
    if not sort:
        return query

    if joined is None:
        joined = set()

    for field in sort.split(","):
        desc = field.startswith("-")
        field_name = field.lstrip("-")

        column, owner_model = _resolve_column(field_name, primary_model, related_models)

        if column is None:
            continue

        if owner_model is not primary_model and owner_model not in joined:
            query = query.join(owner_model)  # type: ignore
            joined.add(owner_model)

        query = query.order_by(column.desc() if desc else column.asc())

    return query


def apply_pagination(query: Query, limit: int = 10, offset: int = 0) -> Query:
    limit = max(1, min(limit, 100))  # clamp: 1–100
    offset = max(0, offset)
    return query.limit(limit).offset(offset)
