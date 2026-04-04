from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Type
from sqlalchemy.orm import Query
from sqlalchemy import and_


def get_or_404(db: Session, model: Type, value, field="id"):
    obj = db.query(model).filter(getattr(model, field) == value).first()

    if not obj:
        raise HTTPException(404, f"{model.__name__} not found")
    return obj


def apply_filters(query: Query, model, filters: dict):
    """
    Apply dynamic filters to a SQLAlchemy query.

    Supported formats:
    field=value
    field__gt=value
    field__gte=value
    field__lt=value
    field__lte=value
    field__like=value
    field__in=[values]
    """

    for raw_field, value in filters.items():
        if value is None:
            continue

        # Split operator
        if "__" in raw_field:
            field, operator = raw_field.split("__", 1)
        else:
            field, operator = raw_field, "eq"

        if not hasattr(model, field):
            continue

        column = getattr(model, field)

        # Apply operators
        if operator == "eq":
            query = query.filter(column == value)

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

        elif operator == "in" and isinstance(value, list):
            query = query.filter(column.in_(value))

    return query
