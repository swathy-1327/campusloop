from bson import ObjectId
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from services.trust_service import trust_level_from_score
from utils.db import get_db


class UserDocument(dict):
    def check_password(self, raw_password):
        return check_password_hash(self["password_hash"], raw_password)


def _users():
    return get_db().users


def _wrap(user):
    return UserDocument(user) if user else None


def create_user(name, email, phone, password):
    admin_email = current_app.config.get("ADMIN_EMAIL", "admin@gmail.com").lower()
    is_admin = email.lower() == admin_email
    payload = {
        "name": name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "phone": phone,
        "role": "admin" if is_admin else "buyer",
        "account_status": "active",
        "trust_score": 20,
        "trust_level": trust_level_from_score(20),
        "is_verified_seller": False,
        "created_at": current_app.extensions["now"](),
    }
    result = _users().insert_one(payload)
    payload["_id"] = result.inserted_id
    return UserDocument(payload)


def find_user_by_email(email):
    return _wrap(_users().find_one({"email": email}))


def find_user_by_id(user_id):
    return _wrap(_users().find_one({"_id": ObjectId(user_id)}))


def update_user_profile(user_id, name, phone):
    _users().update_one({"_id": ObjectId(user_id)}, {"$set": {"name": name, "phone": phone}})


def list_all_users():
    return list(_users().find().sort("created_at", -1))


def list_users_filtered(role_filter="both", search=""):
    filters = {}
    if role_filter == "seller":
        filters["role"] = "seller"
    elif role_filter == "buyer":
        filters["role"] = "buyer"

    if search:
        filters["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
        ]

    return list(_users().find(filters).sort("created_at", -1))


def admin_update_user_status(user_id, account_status=None, is_verified_seller=None):
    updates = {}
    if account_status is not None:
        updates["account_status"] = account_status
    if is_verified_seller is not None:
        updates["is_verified_seller"] = is_verified_seller
        if is_verified_seller:
            updates["role"] = "seller"
    if updates:
        _users().update_one({"_id": ObjectId(user_id)}, {"$set": updates})


def admin_delete_user(user_id):
    _users().delete_one({"_id": ObjectId(user_id)})
