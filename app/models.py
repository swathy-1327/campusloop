from datetime import datetime

from flask_login import UserMixin

from app import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column("pwd_hash", db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), default="buyer", nullable=False)
    account_status = db.Column("acct_stat", db.String(20), default="active", nullable=False)
    trust_score = db.Column("trust_scr", db.Integer, default=20, nullable=False)
    trust_level = db.Column("trust_lvl", db.String(30), default="New User", nullable=False)
    is_verified_seller = db.Column("seller_ok", db.Boolean, default=False, nullable=False)

    products = db.relationship("Product", back_populates="seller", lazy=True)
    sent_messages = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        backref="sender",
        lazy=True,
    )

    def is_admin(self):
        return self.role == "admin"


class VerificationRequest(TimestampMixin, db.Model):
    __tablename__ = "verification_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    id_type = db.Column(db.String(50), nullable=False)
    id_document_ref = db.Column("id_ref", db.String(255), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    admin_remark = db.Column("admin_note", db.Text)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by_admin = db.Column("admin_id", db.Integer, db.ForeignKey("users.id"))

    user = db.relationship("User", foreign_keys=[user_id], backref="verification_requests")


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ai_generated_description = db.Column("ai_desc", db.Text)
    category = db.Column(db.String(50), nullable=False)
    use_type = db.Column("use_tag", db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    item_condition = db.Column("item_cond", db.String(50), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(255))
    product_status = db.Column("prod_stat", db.String(20), default="available", nullable=False)
    removed_by_admin = db.Column("admin_rm", db.Boolean, default=False, nullable=False)
    removal_reason = db.Column("rm_note", db.String(255))

    seller = db.relationship("User", foreign_keys=[seller_id], back_populates="products")


class Order(TimestampMixin, db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    payment_method = db.Column("pay_mode", db.String(30), nullable=False)
    order_status = db.Column("ord_stat", db.String(20), default="pending", nullable=False)
    completed_at = db.Column(db.DateTime)

    product = db.relationship("Product", backref="orders")
    buyer = db.relationship("User", foreign_keys=[buyer_id], backref="orders_as_buyer")
    seller = db.relationship("User", foreign_keys=[seller_id], backref="orders_as_seller")
    reviews = db.relationship("Review", backref="order", lazy=True)


class RentRequest(TimestampMixin, db.Model):
    __tablename__ = "rent_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_name = db.Column("prod_name", db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    note = db.Column(db.Text)
    status = db.Column(db.String(20), default="open", nullable=False)

    user = db.relationship("User", backref="rent_requests")


class UnavailableProductRequest(TimestampMixin, db.Model):
    __tablename__ = "unavailable_product_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_name = db.Column("prod_name", db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="open", nullable=False)

    user = db.relationship("User", backref="unavailable_requests")


class ChatThread(TimestampMixin, db.Model):
    __tablename__ = "chat_threads"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    product = db.relationship("Product", backref="chat_threads")
    buyer = db.relationship("User", foreign_keys=[buyer_id], backref="buyer_threads")
    seller = db.relationship("User", foreign_keys=[seller_id], backref="seller_threads")


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey("chat_threads.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message_text = db.Column("msg_text", db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    thread = db.relationship("ChatThread", backref="messages")


class Review(TimestampMixin, db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    from_user = db.relationship("User", foreign_keys=[from_user_id], backref="reviews_written")
    to_user = db.relationship("User", foreign_keys=[to_user_id], backref="reviews_received")


class TrustLog(db.Model):
    __tablename__ = "trust_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    score_change = db.Column("score_chg", db.Integer, nullable=False)
    action_type = db.Column("act_type", db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref="trust_logs")


class Report(TimestampMixin, db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    reported_by = db.Column("report_by", db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_type = db.Column("target_tp", db.String(30), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="open", nullable=False)
    reviewed_by_admin = db.Column("admin_id", db.Integer, db.ForeignKey("users.id"))
