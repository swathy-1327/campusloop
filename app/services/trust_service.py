from app import db
from app.models import TrustLog


TRUST_LEVELS = [
    (75, "Highly Trusted"),
    (50, "Trusted Seller"),
    (30, "Basic Verified"),
    (0, "New User"),
]


def derive_level(score):
    for threshold, label in TRUST_LEVELS:
        if score >= threshold:
            return label
    return "New User"


def apply_trust_change(user, score_change, reason, action_type):
    user.trust_score = max(0, user.trust_score + score_change)
    user.trust_level = derive_level(user.trust_score)
    db.session.add(
        TrustLog(
            user_id=user.id,
            reason=reason,
            score_change=score_change,
            action_type=action_type,
        )
    )
