from bson import ObjectId
from flask import current_app

from utils.db import get_db


def _products():
    return get_db().products


def create_product(
    seller_id,
    title,
    category,
    use_type,
    price,
    condition,
    mode,
    image_urls,
    description,
    ai_generated_description,
):
    payload = {
        "seller_id": seller_id,
        "title": title,
        "description": description,
        "ai_generated_description": ai_generated_description,
        "category": category,
        "use_type": use_type,
        "price": price,
        "condition": condition,
        "mode": mode,
        "image_urls": image_urls,
        "product_status": "active",
        "created_at": current_app.extensions["now"](),
        "updated_at": current_app.extensions["now"](),
        "removed_by_admin": False,
        "removal_reason": "",
    }
    result = _products().insert_one(payload)
    payload["_id"] = result.inserted_id
    return payload


def list_marketplace_products(query="", category="", mode="", limit=None, include_inactive=False):
    filters = {}
    if not include_inactive:
        filters["product_status"] = "active"
    if query:
        filters["title"] = {"$regex": query, "$options": "i"}
    if category:
        filters["category"] = category
    if mode:
        filters["mode"] = mode

    cursor = _products().find(filters).sort("created_at", -1)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)


def list_products_for_seller(seller_id):
    return list(_products().find({"seller_id": seller_id}).sort("created_at", -1))


def find_product_by_id(product_id):
    return _products().find_one({"_id": ObjectId(product_id)})


def admin_update_product_status(product_id, product_status, removal_reason=""):
    _products().update_one(
        {"_id": ObjectId(product_id)},
        {
            "$set": {
                "product_status": product_status,
                "removed_by_admin": product_status != "active",
                "removal_reason": removal_reason,
                "updated_at": current_app.extensions["now"](),
            }
        },
    )


def admin_edit_product(product_id, title, category, use_type, price, condition, mode, description):
    _products().update_one(
        {"_id": ObjectId(product_id)},
        {
            "$set": {
                "title": title,
                "category": category,
                "use_type": use_type,
                "price": price,
                "condition": condition,
                "mode": mode,
                "description": description,
                "updated_at": current_app.extensions["now"](),
            }
        },
    )


def admin_delete_product(product_id):
    _products().delete_one({"_id": ObjectId(product_id)})
