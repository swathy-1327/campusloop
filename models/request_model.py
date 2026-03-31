from flask import current_app

from utils.db import get_db


def _rent_requests():
    return get_db().rent_requests


def _unavailable_requests():
    return get_db().unavailable_product_requests


def create_rent_request(user_id, product_name, category, duration, budget, note):
    payload = {
        "user_id": user_id,
        "product_name": product_name,
        "category": category,
        "duration": duration,
        "budget": budget,
        "note": note,
        "status": "open",
        "created_at": current_app.extensions["now"](),
    }
    _rent_requests().insert_one(payload)
    return payload


def create_unavailable_request(user_id, product_name, category, budget, description):
    payload = {
        "user_id": user_id,
        "product_name": product_name,
        "category": category,
        "budget": budget,
        "description": description,
        "status": "open",
        "created_at": current_app.extensions["now"](),
    }
    _unavailable_requests().insert_one(payload)
    return payload


def list_requests_for_user(user_id):
    return {
        "rent_requests": list(_rent_requests().find({"user_id": user_id}).sort("created_at", -1)),
        "unavailable_requests": list(
            _unavailable_requests().find({"user_id": user_id}).sort("created_at", -1)
        ),
    }
