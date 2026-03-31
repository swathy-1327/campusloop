from datetime import datetime, timezone

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from services.trust_service import trust_level_from_score


MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "campusloop"


def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    now = datetime.now(timezone.utc)

    admin = {
        "name": "Campus Admin",
        "email": "admin@campusloop.local",
        "password_hash": generate_password_hash("admin123"),
        "phone": "9999999999",
        "role": "admin",
        "account_status": "active",
        "trust_score": 75,
        "trust_level": trust_level_from_score(75),
        "is_verified_seller": False,
        "created_at": now,
    }
    seller = {
        "name": "Aarav Seller",
        "email": "seller@campusloop.local",
        "password_hash": generate_password_hash("seller123"),
        "phone": "8888888888",
        "role": "seller",
        "account_status": "active",
        "trust_score": 55,
        "trust_level": trust_level_from_score(55),
        "is_verified_seller": True,
        "created_at": now,
    }
    buyer = {
        "name": "Maya Buyer",
        "email": "buyer@campusloop.local",
        "password_hash": generate_password_hash("buyer123"),
        "phone": "7777777777",
        "role": "buyer",
        "account_status": "active",
        "trust_score": 24,
        "trust_level": trust_level_from_score(24),
        "is_verified_seller": False,
        "created_at": now,
    }

    db.users.delete_many({"email": {"$in": [admin["email"], seller["email"], buyer["email"]]}})
    admin_id = db.users.insert_one(admin).inserted_id
    seller_id = db.users.insert_one(seller).inserted_id
    buyer_id = db.users.insert_one(buyer).inserted_id

    db.products.delete_many({"seller_id": str(seller_id)})
    db.products.insert_many(
        [
            {
                "seller_id": str(seller_id),
                "title": "Engineering Mathematics Textbook",
                "description": "Used for one semester. Clean pages and useful solved examples.",
                "ai_generated_description": "Engineering Mathematics Textbook in good condition, ready for a new owner and ideal for first-year coursework.",
                "category": "Books",
                "use_type": "Semester study",
                "price": 450.0,
                "condition": "Good",
                "mode": "sale",
                "image_urls": [],
                "product_status": "active",
                "created_at": now,
                "updated_at": now,
                "removed_by_admin": False,
                "removal_reason": "",
            },
            {
                "seller_id": str(seller_id),
                "title": "Scientific Calculator",
                "description": "Available for short-term rent during exam period.",
                "ai_generated_description": "Scientific Calculator in excellent condition, available for temporary campus use for exams and lab sessions.",
                "category": "Electronics",
                "use_type": "Exam support",
                "price": 150.0,
                "condition": "Excellent",
                "mode": "rent",
                "image_urls": [],
                "product_status": "active",
                "created_at": now,
                "updated_at": now,
                "removed_by_admin": False,
                "removal_reason": "",
            },
        ]
    )

    print("Seed complete.")
    print(f"Admin: admin@campusloop.local / admin123 ({admin_id})")
    print(f"Seller: seller@campusloop.local / seller123 ({seller_id})")
    print(f"Buyer: buyer@campusloop.local / buyer123 ({buyer_id})")


if __name__ == "__main__":
    main()
