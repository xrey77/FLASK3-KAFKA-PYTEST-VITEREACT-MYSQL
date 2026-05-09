import math
from sqlalchemy import select, func, or_ # type: ignore
from config.extensions import db
from app.models.product import Products
from app.models.sale import Sales
from werkzeug.exceptions import NotFound # type: ignore
from flask import abort # type: ignore

def get_paginated_products(page, per_page=5):

    total_records = db.session.query(func.count()).select_from(Products).scalar()
    total_pages = math.ceil(total_records / per_page)
    
    pagination = db.paginate(
        db.select(Products).order_by(Products.id), 
        page=page, 
        per_page=per_page, 
        error_out=False
    )

    if not pagination.total:
        return None

    return {
        "page": page,
        "totpage": total_pages,
        "totalrecords": total_records,
        "products": [item.to_dict() for item in pagination.items]
    }


def get_product_search_results(page, keyword, per_page=5):
    search = f"%{keyword.lower()}%"
    
    # Base search filter
    search_filter = or_(Products.descriptions.ilike(search))

    # Count total records
    tot_records = db.session.query(func.count()) \
        .select_from(Products) \
        .where(search_filter) \
        .scalar()

    total_pages = math.ceil(tot_records / per_page)

    # Paginate results
    stmt = select(Products).where(search_filter).order_by(Products.id)
    pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)
    
    products = [item.to_dict() for item in pagination.items]

    return {
        "page": page,
        "totpage": total_pages,
        "totalrecords": tot_records,
        "products": products
    }


def get_all_sales_service():
    query = db.select(Sales)
    sales_records = db.session.execute(query).scalars().all()

    if not sales_records:
        return None

    sales_list = []
    for sale in sales_records:
        sales_list.append({
            "id": sale.id,
            "salesamount": sale.salesamount,
            "salesdate": sale.salesdate.isoformat() if sale.salesdate else None
        })

    return sales_list
