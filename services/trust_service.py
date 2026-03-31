from datetime import datetime, timezone

from bson import ObjectId

from utils.db import get_db


TRUST_EVENTS = {
    "seller_verification_approved": ("Seller verification approved", 30, "bonus"),
    "successful_sale": ("Successful sale completed", 5, "bonus"),
    "successful_purchase": ("Successful purchase completed", 2, "bonus"),
    "rental_completed": ("Rental completed properly", 4, "bonus"),
    "positive_review": ("Positive review received", 3, "bonus"),
    "fake_listing": ("Fake listing reported", -15, "penalty"),
    "repeated_cancellation": ("Repeated cancellation detected", -5, "penalty"),
    "valid_complaint": ("Valid complaint received", -10, "penalty"),
    "suspicious_activity": ("Suspicious activity detected", -20, "penalty"),
}


def trust_level_from_score(score):
    if score >= 75:
        return "Highly Trusted"
    if score >= 50:
        return "Trusted Seller"
    if score >= 30:
        return "Basic Verified"
    return "New User"


def apply_trust_event(user_id, event_key):
    if event_key not in TRUST_EVENTS:
        return None

    reason, score_change, action_type = TRUST_EVENTS[event_key]
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    new_score = max(0, user.get("trust_score", 20) + score_change)
    trust_level = trust_level_from_score(new_score)
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"trust_score": new_score, "trust_level": trust_level}},
    )
    db.trust_logs.insert_one(
        {
            "user_id": user_id,
            "reason": reason,
            "score_change": score_change,
            "action_type": action_type,
            "created_at": datetime.now(timezone.utc),
        }
    )
    return {"trust_score": new_score, "trust_level": trust_level}
