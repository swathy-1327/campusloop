from flask import current_app

from utils.db import get_db


def _orders():
    return get_db().orders


def create_order(product_id, buyer_id, seller_id, payment_method):
    payload = {
        "product_id": product_id,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "payment_method": payment_method,
        "order_status": "placed",
        "created_at": current_app.extensions["now"](),
        "completed_at": None,
    }
    result = _orders().insert_one(payload)
    payload["_id"] = result.inserted_id
    return payload


def list_orders_for_user(user_id):
    return list(
        _orders()
        .find({"$or": [{"buyer_id": user_id}, {"seller_id": user_id}]})
        .sort("created_at", -1)
    )
