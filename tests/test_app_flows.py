import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

import mongomock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SECRET_KEY"] = "campusloop-test-secret"
os.environ["MONGO_URI"] = "mongodb://localhost/campusloop-test"

# Replace PyMongo before importing the app so even its module-level app uses a
# disposable in-memory database. Tests never connect to Atlas.
import utils.db

_bootstrap_client = mongomock.MongoClient()
utils.db.MongoClient = lambda *args, **kwargs: _bootstrap_client

import app as app_module
from models.user_model import create_user


class CampusLoopFlowTests(unittest.TestCase):
    def setUp(self):
        self.mongo = mongomock.MongoClient()
        self.db = self.mongo["campusloop"]

        def init_test_db(app):
            app.extensions["mongo_client"] = self.mongo
            app.extensions["mongo_db"] = self.db
            app.extensions["now"] = lambda: datetime.now(timezone.utc)
            self.db.users.create_index("email", unique=True)

        app_module.init_db = init_test_db
        self.app = app_module.create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()
        self.admin = self.make_user("admin@example.test", role="admin")
        self.seller = self.make_user(
            "seller@example.test", role="seller", is_verified_seller=True
        )
        self.buyer = self.make_user("buyer@example.test")

    def make_user(self, email, role="buyer", is_verified_seller=False):
        with self.app.app_context():
            user = create_user("Test User", email, "5550100", "test-password")
            self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"role": role, "is_verified_seller": is_verified_seller}},
            )
            user.update(role=role, is_verified_seller=is_verified_seller)
            return user

    def login(self, client, user):
        return client.post(
            "/login",
            data={"email": user["email"], "password": "test-password"},
        )

    def test_public_pages_and_anonymous_guards(self):
        for path in ("/", "/login", "/register", "/products/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

        for path in (
            "/products/dashboard",
            "/requests/",
            "/requests/rent",
            "/requests/unavailable",
            "/profile",
            "/admin/seller-verification",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login", response.headers["Location"])
        self.assertEqual(self.client.get("/products/not-an-object-id").status_code, 302)

    def test_register_login_profile_and_blocked_account(self):
        response = self.client.post(
            "/register",
            data={
                "name": "New Student",
                "email": "NEW@example.test",
                "phone": "5550101",
                "password": "new-password",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(self.db.users.find_one({"email": "new@example.test"}))

        duplicate = self.client.post(
            "/register",
            data={
                "name": "New Student",
                "email": "new@example.test",
                "phone": "5550101",
                "password": "new-password",
            },
        )
        self.assertEqual(duplicate.status_code, 200)
        self.assertIn(b"already exists", duplicate.data)

        self.assertEqual(self.login(self.client, self.buyer).status_code, 302)
        profile = self.client.post(
            "/profile", data={"name": "Updated Student", "phone": "5550102"}
        )
        self.assertEqual(profile.status_code, 302)
        self.assertEqual(
            self.db.users.find_one({"_id": self.buyer["_id"]})["name"],
            "Updated Student",
        )

        self.db.users.update_one(
            {"_id": self.buyer["_id"]}, {"$set": {"account_status": "blocked"}}
        )
        protected = self.client.get("/products/dashboard")
        self.assertEqual(protected.status_code, 302)
        blocked_login = self.client.post(
            "/login",
            data={"email": self.buyer["email"], "password": "test-password"},
        )
        self.assertEqual(blocked_login.status_code, 200)
        self.assertIn(b"account is blocked", blocked_login.data)

    def test_seller_verification_and_listing_lifecycle(self):
        self.login(self.client, self.buyer)
        submitted = self.client.post(
            "/admin/seller-verification",
            data={"id_type": "Student ID", "id_document_url": "https://example.test/id"},
        )
        self.assertEqual(submitted.status_code, 302)
        verification = self.db.verification_requests.find_one(
            {"user_id": str(self.buyer["_id"])}
        )
        self.assertEqual(verification["status"], "pending")

        admin_client = self.app.test_client()
        self.login(admin_client, self.admin)
        self.assertEqual(admin_client.get("/admin/dashboard").status_code, 200)
        approved = admin_client.post(
            f"/admin/verification/{verification['_id']}/review",
            data={"decision": "approved", "remark": "Verified"},
        )
        self.assertEqual(approved.status_code, 302)
        updated_buyer = self.db.users.find_one({"_id": self.buyer["_id"]})
        self.assertTrue(updated_buyer["is_verified_seller"])
        self.assertEqual(updated_buyer["role"], "seller")

        listing = self.client.post(
            "/products/new",
            data={
                "title": "Calculus book",
                "category": "Books",
                "use_type": "Semester study",
                "price": "120.50",
                "condition": "Good",
                "mode": "sale",
                "description": "Clean copy",
                "use_ai": "no",
            },
        )
        self.assertEqual(listing.status_code, 302)
        product = self.db.products.find_one({"title": "Calculus book"})
        self.assertEqual(product["price"], 120.5)
        self.assertEqual(
            self.client.get("/products/?q=calculus&category=Books&mode=sale").status_code,
            200,
        )
        self.assertEqual(
            self.client.get(f"/products/{product['_id']}").status_code, 200
        )

        admin_client.post(
            f"/admin/products/{product['_id']}/status",
            data={"product_status": "hidden", "removal_reason": "Review"},
        )
        self.assertEqual(self.client.get(f"/products/{product['_id']}").status_code, 302)

    def test_buy_chat_and_request_workflows(self):
        product = self.db.products.insert_one(
            {
                "seller_id": str(self.seller["_id"]),
                "title": "Lab coat",
                "description": "Clean",
                "ai_generated_description": "",
                "category": "Lab Items",
                "use_type": "Lab",
                "price": 75.0,
                "condition": "Good",
                "mode": "sale",
                "image_urls": [],
                "product_status": "active",
                "created_at": datetime.now(timezone.utc),
            }
        ).inserted_id

        self.login(self.client, self.buyer)
        self.assertEqual(
            self.client.post(
                f"/products/{product}/buy", data={"payment_method": "UPI"}
            ).status_code,
            302,
        )
        self.assertEqual(self.db.orders.count_documents({"product_id": str(product)}), 1)

        chat_response = self.client.post(
            f"/chat/product/{product}/{self.seller['_id']}",
            data={"message_text": "Is this available?"},
        )
        self.assertEqual(chat_response.status_code, 302)
        chat = self.db.chats.find_one({"product_id": str(product)})
        self.assertEqual(chat["messages"][0]["message_text"], "Is this available?")
        thread = self.client.get(f"/chat/thread/{chat['_id']}")
        self.assertEqual(thread.status_code, 200)

        rent = self.client.post(
            "/requests/rent",
            data={
                "product_name": "Tripod",
                "category": "Electronics",
                "duration": "One week",
                "budget": "20",
            },
        )
        self.assertEqual(rent.status_code, 302)
        unavailable = self.client.post(
            "/requests/unavailable",
            data={"product_name": "Soldering iron", "category": "Lab Items", "budget": "30"},
        )
        self.assertEqual(unavailable.status_code, 302)
        self.assertEqual(self.client.get("/requests/").status_code, 200)

    def test_invalid_amounts_and_hidden_products_do_not_create_records(self):
        self.login(self.client, self.buyer)
        for path, data in (
            (
                "/requests/rent",
                {"product_name": "Tripod", "category": "Electronics", "duration": "1 week", "budget": "NaN"},
            ),
            (
                "/requests/unavailable",
                {"product_name": "Adapter", "category": "Electronics", "budget": "-1"},
            ),
        ):
            with self.subTest(path=path):
                response = self.client.post(path, data=data)
                self.assertEqual(response.status_code, 200)
        self.assertEqual(self.db.rent_requests.count_documents({}), 0)
        self.assertEqual(self.db.unavailable_product_requests.count_documents({}), 0)

        seller_client = self.app.test_client()
        self.login(seller_client, self.seller)
        invalid_listing = seller_client.post(
            "/products/new",
            data={
                "title": "Bad price",
                "category": "Books",
                "use_type": "Study",
                "price": "Infinity",
                "condition": "Good",
                "mode": "sale",
                "description": "Invalid amount",
                "use_ai": "no",
            },
        )
        self.assertEqual(invalid_listing.status_code, 200)
        self.assertEqual(self.db.products.count_documents({}), 0)

        hidden = self.db.products.insert_one(
            {
                "seller_id": str(self.seller["_id"]),
                "product_status": "hidden",
                "title": "Hidden item",
                "category": "Books",
                "mode": "sale",
                "price": 1,
                "image_urls": [],
                "description": "Hidden",
            }
        ).inserted_id
        self.client.post(f"/products/{hidden}/buy")
        self.assertEqual(self.db.orders.count_documents({}), 0)

    def test_chat_rejects_a_forged_seller_id_and_admin_is_restricted(self):
        product_id = self.db.products.insert_one(
            {"seller_id": str(self.seller["_id"]), "product_status": "active"}
        ).inserted_id
        self.login(self.client, self.buyer)
        response = self.client.post(
            f"/chat/product/{product_id}/{self.admin['_id']}",
            data={"message_text": "Wrong recipient"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.db.chats.count_documents({}), 0)
        self.assertEqual(self.client.get("/admin/dashboard").status_code, 302)

    def test_admin_moderates_users_and_products(self):
        product_id = self.db.products.insert_one(
            {
                "seller_id": str(self.seller["_id"]),
                "title": "Moderated item",
                "description": "Item to review",
                "ai_generated_description": "",
                "category": "Books",
                "use_type": "Study",
                "price": 30.0,
                "condition": "Good",
                "mode": "sale",
                "image_urls": [],
                "product_status": "active",
                "created_at": datetime.now(timezone.utc),
            }
        ).inserted_id
        admin_client = self.app.test_client()
        self.login(admin_client, self.admin)

        updated = admin_client.post(
            f"/admin/products/{product_id}/edit",
            data={
                "title": "Updated item",
                "category": "Books",
                "use_type": "Study",
                "price": "42.5",
                "condition": "Good",
                "mode": "rent",
                "description": "Updated details",
            },
        )
        self.assertEqual(updated.status_code, 302)
        self.assertEqual(self.db.products.find_one({"_id": product_id})["price"], 42.5)

        blocked = admin_client.post(
            f"/admin/users/{self.buyer['_id']}/status",
            data={"account_status": "blocked"},
        )
        self.assertEqual(blocked.status_code, 302)
        self.assertEqual(
            self.db.users.find_one({"_id": self.buyer["_id"]})["account_status"],
            "blocked",
        )

        invalid_state = admin_client.post(
            f"/admin/products/{product_id}/status",
            data={"product_status": "deleted"},
        )
        self.assertEqual(invalid_state.status_code, 302)
        self.assertEqual(
            self.db.products.find_one({"_id": product_id})["product_status"],
            "active",
        )

        admin_client.post(
            f"/admin/users/{self.seller['_id']}/status",
            data={"account_status": "blocked"},
        )
        self.assertEqual(
            self.db.products.find_one({"_id": product_id})["product_status"],
            "hidden",
        )
        admin_client.post(
            f"/admin/users/{self.seller['_id']}/status",
            data={"account_status": "active"},
        )
        self.assertEqual(
            self.db.products.find_one({"_id": product_id})["product_status"],
            "active",
        )

        chat_buyer = self.make_user("chat-reader@example.test")
        chat_id = self.db.chats.insert_one(
            {
                "product_id": str(product_id),
                "buyer_id": str(chat_buyer["_id"]),
                "seller_id": str(self.seller["_id"]),
                "messages": [],
                "created_at": datetime.now(timezone.utc),
            }
        ).inserted_id
        removed = admin_client.post(f"/admin/users/{self.seller['_id']}/delete")
        self.assertEqual(removed.status_code, 302)
        self.assertIsNone(self.db.users.find_one({"_id": self.seller["_id"]}))
        self.assertEqual(
            self.db.products.find_one({"_id": product_id})["product_status"],
            "hidden",
        )

        buyer_client = self.app.test_client()
        self.login(buyer_client, chat_buyer)
        archived_chat = buyer_client.get(f"/chat/thread/{chat_id}")
        self.assertEqual(archived_chat.status_code, 200)
        self.assertIn(b"read-only", archived_chat.data)
        self.assertEqual(
            buyer_client.post(
                f"/chat/thread/{chat_id}", data={"message_text": "Reply"}
            ).status_code,
            302,
        )


if __name__ == "__main__":
    unittest.main()
