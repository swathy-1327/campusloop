from bson import ObjectId
from flask import current_app

from utils.db import get_db


def _verification_requests():
    return get_db().verification_requests


def create_verification_request(user_id, id_type, id_document_url):
    payload = {
        "user_id": user_id,
        "id_type": id_type,
        "id_document_url": id_document_url,
        "status": "pending",
        "admin_remark": "",
        "submitted_at": current_app.extensions["now"](),
        "reviewed_at": None,
        "reviewed_by_admin": None,
    }
    _verification_requests().insert_one(payload)
    return payload


def list_requests_for_user(user_id):
    return list(_verification_requests().find({"user_id": user_id}).sort("submitted_at", -1))


def get_pending_requests():
    return list(_verification_requests().find({"status": "pending"}).sort("submitted_at", 1))


def review_verification_request(request_id, decision, remark, admin_id):
    _verification_requests().update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "status": decision,
                "admin_remark": remark,
                "reviewed_at": current_app.extensions["now"](),
                "reviewed_by_admin": admin_id,
            }
        },
    )
    return _verification_requests().find_one({"_id": ObjectId(request_id)})
