from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.chat_model import get_recent_chats_for_user
from models.order_model import create_order, list_orders_for_user
from models.product_model import create_product, find_product_by_id, list_marketplace_products, list_products_for_seller
from models.user_model import find_user_by_id
from services.ai_description_service import generate_product_description
from services.trust_service import apply_trust_event
from utils.auth import current_user, login_required, seller_required

product_bp = Blueprint("product", __name__, url_prefix="/products")


@product_bp.app_context_processor
def inject_global_user():
    return {"current_user": current_user()}


@product_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    return render_template(
        "dashboard.html",
        products=list_products_for_seller(str(user["_id"])),
        orders=list_orders_for_user(str(user["_id"])),
        chats=get_recent_chats_for_user(str(user["_id"])),
        marketplace_products=list_marketplace_products(limit=6),
    )


@product_bp.route("/")
def marketplace():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    mode = request.args.get("mode", "").strip()
    products = list_marketplace_products(query=query, category=category, mode=mode)
    return render_template(
        "marketplace.html",
        products=products,
        query=query,
        selected_category=category,
        selected_mode=mode,
    )


@product_bp.route("/new", methods=["GET", "POST"])
@seller_required
def add_product():
    if request.method == "POST":
        user = current_user()
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        use_type = request.form.get("use_type", "").strip()
        price = request.form.get("price", "").strip()
        condition = request.form.get("condition", "").strip()
        mode = request.form.get("mode", "").strip()
        image_urls = request.form.get("image_urls", "").strip()
        description = request.form.get("description", "").strip()
        use_ai = request.form.get("use_ai") == "yes"

        if not all([title, category, use_type, price, condition, mode]):
            flash("Please complete all required product details.", "error")
            return render_template("add_product.html")

        ai_description = ""
        if use_ai:
            ai_description = generate_product_description(title, category, condition, mode)
            if not description:
                description = ai_description

        create_product(
            seller_id=str(user["_id"]),
            title=title,
            category=category,
            use_type=use_type,
            price=float(price),
            condition=condition,
            mode=mode,
            image_urls=[item.strip() for item in image_urls.split(",") if item.strip()],
            description=description,
            ai_generated_description=ai_description,
        )
        flash("Product listed successfully.", "success")
        return redirect(url_for("product.dashboard"))

    return render_template("add_product.html")


@product_bp.route("/<product_id>")
def product_detail(product_id):
    product = find_product_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("product.marketplace"))

    seller = find_user_by_id(product["seller_id"])
    return render_template("product_detail.html", product=product, seller=seller)


@product_bp.route("/<product_id>/buy", methods=["POST"])
@login_required
def buy_product(product_id):
    user = current_user()
    product = find_product_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("product.marketplace"))
    if product["seller_id"] == str(user["_id"]):
        flash("You cannot buy your own product.", "error")
        return redirect(url_for("product.product_detail", product_id=product_id))

    order = create_order(
        product_id=product_id,
        buyer_id=str(user["_id"]),
        seller_id=product["seller_id"],
        payment_method=request.form.get("payment_method", "Cash on meetup"),
    )
    apply_trust_event(product["seller_id"], "successful_sale")
    apply_trust_event(str(user["_id"]), "successful_purchase")
    flash(f"Order created with status {order['order_status']}.", "success")
    return redirect(url_for("product.dashboard"))
