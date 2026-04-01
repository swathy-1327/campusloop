from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import ChatThread, Order, Product, Review
from app.services.ai_service import generate_product_description
from app.services.trust_service import apply_trust_change


marketplace_bp = Blueprint("marketplace", __name__)


@marketplace_bp.route("/")
def browse():
    query = Product.query.filter(
        Product.removed_by_admin.is_(False),
        Product.product_status.in_(["available", "sold"]),
    )

    keyword = request.args.get("keyword", "").strip() or request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    mode = request.args.get("mode", "").strip()

    if keyword:
        query = query.filter(Product.title.ilike(f"%{keyword}%"))
    if category:
        query = query.filter_by(category=category)
    if mode:
        query = query.filter_by(mode=mode)

    products = query.order_by(Product.created_at.desc()).all()
    return render_template(
        "marketplace/browse.html",
        products=products,
        query=keyword,
        selected_category=category,
        selected_mode=mode,
    )


@marketplace_bp.route("/dashboard")
@login_required
def dashboard():
    seller_products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).all()
    user_orders = Order.query.filter(
        (Order.buyer_id == current_user.id) | (Order.seller_id == current_user.id)
    ).order_by(Order.created_at.desc()).all()
    chats = ChatThread.query.filter(
        (ChatThread.buyer_id == current_user.id) | (ChatThread.seller_id == current_user.id)
    ).order_by(ChatThread.created_at.desc()).all()
    marketplace_products = (
        Product.query.filter(
            Product.removed_by_admin.is_(False),
            Product.product_status == "available",
        )
        .order_by(Product.created_at.desc())
        .limit(6)
        .all()
    )
    return render_template(
        "marketplace/dashboard.html",
        products=seller_products,
        orders=user_orders,
        chats=chats,
        marketplace_products=marketplace_products,
    )


@marketplace_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.join(Order).filter(Order.product_id == product.id).order_by(Review.created_at.desc()).all()
    return render_template("marketplace/product_detail.html", product=product, reviews=reviews)


@marketplace_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product():
    if not current_user.is_verified_seller:
        flash("Only verified sellers can create listings.", "warning")
        return redirect(url_for("verification.become_seller"))

    if request.method == "POST":
        title = request.form["title"].strip()
        category = request.form["category"].strip()
        item_condition = request.form["item_condition"].strip()
        mode = request.form["mode"].strip()
        description = request.form["description"].strip()
        ai_description = generate_product_description(title, category, item_condition, mode)

        product = Product(
            seller_id=current_user.id,
            title=title,
            description=description,
            ai_generated_description=ai_description,
            category=category,
            use_type=request.form["use_type"].strip(),
            price=request.form["price"],
            item_condition=item_condition,
            mode=mode,
            image_url=request.form.get("image_url", "").strip() or None,
        )
        db.session.add(product)
        db.session.commit()
        flash("Product listed successfully.", "success")
        return redirect(url_for("marketplace.product_detail", product_id=product.id))

    return render_template("marketplace/add_product.html")


@marketplace_bp.route("/my-listings")
@login_required
def my_listings():
    products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).all()
    return render_template("marketplace/my_listings.html", products=products)


@marketplace_bp.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        flash("You can edit only your own listings.", "danger")
        return redirect(url_for("marketplace.product_detail", product_id=product.id))

    if request.method == "POST":
        product.title = request.form["title"].strip()
        product.category = request.form["category"].strip()
        product.use_type = request.form["use_type"].strip()
        product.item_condition = request.form["item_condition"].strip()
        product.mode = request.form["mode"].strip()
        product.price = request.form["price"]
        product.image_url = request.form.get("image_url", "").strip() or None
        product.description = request.form["description"].strip()
        product.ai_generated_description = generate_product_description(
            product.title,
            product.category,
            product.item_condition,
            product.mode,
        )
        db.session.commit()
        flash("Listing updated successfully.", "success")
        return redirect(url_for("marketplace.product_detail", product_id=product.id))

    return render_template("marketplace/edit_product.html", product=product)


@marketplace_bp.route("/product/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        flash("You can delete only your own listings.", "danger")
        return redirect(url_for("marketplace.product_detail", product_id=product.id))

    product.product_status = "deleted"
    product.removed_by_admin = False
    product.removal_reason = "Deleted by seller"
    db.session.commit()
    flash("Listing deleted.", "info")
    return redirect(url_for("marketplace.my_listings"))


@marketplace_bp.route("/buy/<int:product_id>", methods=["POST"])
@login_required
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.product_status != "available":
        flash("This listing is no longer available.", "warning")
        return redirect(url_for("marketplace.product_detail", product_id=product.id))

    if product.seller_id == current_user.id:
        flash("You cannot buy your own listing.", "warning")
        return redirect(url_for("marketplace.product_detail", product_id=product.id))

    order = Order(
        product_id=product.id,
        buyer_id=current_user.id,
        seller_id=product.seller_id,
        payment_method=request.form["payment_method"],
        order_status="placed",
        completed_at=None,
    )

    db.session.add(order)
    apply_trust_change(product.seller, 5, "Successful sale", "sale")
    apply_trust_change(current_user, 2, "Successful purchase", "purchase")
    db.session.commit()

    flash("Order placed successfully.", "success")
    return redirect(url_for("marketplace.product_detail", product_id=product.id))


@marketplace_bp.route("/orders")
@login_required
def orders():
    buyer_orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).all()
    seller_orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("marketplace/orders.html", buyer_orders=buyer_orders, seller_orders=seller_orders)


@marketplace_bp.route("/orders/<int:order_id>/review", methods=["POST"])
@login_required
def submit_review(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.id != order.buyer_id:
        flash("Only the buyer can submit a review for this order.", "danger")
        return redirect(url_for("marketplace.orders"))

    existing_review = Review.query.filter_by(order_id=order.id, from_user_id=current_user.id).first()
    if existing_review:
        flash("You have already reviewed this order.", "warning")
        return redirect(url_for("marketplace.orders"))

    rating = int(request.form["rating"])
    review = Review(
        order_id=order.id,
        from_user_id=current_user.id,
        to_user_id=order.seller_id,
        rating=rating,
        comment=request.form.get("comment", "").strip(),
    )
    db.session.add(review)
    if rating >= 4:
        apply_trust_change(order.seller, 3, "Positive review received", "review")
    db.session.commit()
    flash("Review submitted.", "success")
    return redirect(url_for("marketplace.orders"))


@marketplace_bp.route("/start-chat/<int:product_id>", methods=["POST"])
@login_required
def start_chat(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id == current_user.id:
        flash("You already own this listing.", "info")
        return redirect(url_for("marketplace.product_detail", product_id=product_id))

    thread = ChatThread.query.filter_by(
        product_id=product_id,
        buyer_id=current_user.id,
        seller_id=product.seller_id,
    ).first()

    if not thread:
        thread = ChatThread(
            product_id=product_id,
            buyer_id=current_user.id,
            seller_id=product.seller_id,
        )
        db.session.add(thread)
        db.session.commit()

    return redirect(url_for("chat.thread_detail", thread_id=thread.id))
