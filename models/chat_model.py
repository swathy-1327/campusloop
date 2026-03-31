from bson import ObjectId
from flask import current_app

from utils.db import get_db


def _chats():
    return get_db().chats


def get_chat_for_product_users(product_id, buyer_id, seller_id):
    return _chats().find_one(
        {"product_id": product_id, "buyer_id": buyer_id, "seller_id": seller_id}
    )


def get_chat_by_id(chat_id):
    return _chats().find_one({"_id": ObjectId(chat_id)})


def create_or_append_message(product_id, buyer_id, seller_id, sender_id, message_text):
    timestamp = current_app.extensions["now"]()
    message = {"sender_id": sender_id, "message_text": message_text, "sent_at": timestamp}
    chat = get_chat_for_product_users(product_id, buyer_id, seller_id)
    if chat:
        _chats().update_one({"_id": chat["_id"]}, {"$push": {"messages": message}})
        return get_chat_by_id(str(chat["_id"]))
    else:
        result = _chats().insert_one(
            {
                "product_id": product_id,
                "buyer_id": buyer_id,
                "seller_id": seller_id,
                "messages": [message],
                "created_at": timestamp,
            }
        )
        return get_chat_by_id(str(result.inserted_id))


def get_recent_chats_for_user(user_id):
    return list(
        _chats()
        .find({"$or": [{"buyer_id": user_id}, {"seller_id": user_id}]})
        .sort("created_at", -1)
    )
