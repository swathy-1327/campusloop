from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.chat_model import create_or_append_message, get_chat_by_id, get_chat_for_product_users
from models.product_model import find_product_by_id
from models.user_model import find_user_by_id
from utils.auth import current_user, login_required

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.route("/product/<product_id>/<seller_id>", methods=["GET", "POST"])
@login_required
def product_chat(product_id, seller_id):
    user = current_user()
    product = find_product_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("product.marketplace"))

    if request.method == "POST":
        message_text = request.form.get("message_text", "").strip()
        if message_text:
            chat = create_or_append_message(
                product_id=product_id,
                buyer_id=str(user["_id"]),
                seller_id=seller_id,
                sender_id=str(user["_id"]),
                message_text=message_text,
            )
            flash("Message sent.", "success")
            return redirect(url_for("chat.chat_thread", chat_id=chat["_id"]))
        return redirect(url_for("chat.product_chat", product_id=product_id, seller_id=seller_id))

    return render_template(
        "chat.html",
        chat=get_chat_for_product_users(product_id, str(user["_id"]), seller_id),
        product=product,
        seller=find_user_by_id(seller_id),
    )


@chat_bp.route("/thread/<chat_id>", methods=["GET", "POST"])
@login_required
def chat_thread(chat_id):
    chat = get_chat_by_id(chat_id)
    if not chat:
        flash("Conversation not found.", "error")
        return redirect(url_for("product.dashboard"))

    user = current_user()
    if str(user["_id"]) not in {chat["buyer_id"], chat["seller_id"]}:
        flash("You do not have access to this conversation.", "error")
        return redirect(url_for("product.dashboard"))

    if request.method == "POST":
        message_text = request.form.get("message_text", "").strip()
        if message_text:
            create_or_append_message(
                product_id=chat["product_id"],
                buyer_id=chat["buyer_id"],
                seller_id=chat["seller_id"],
                sender_id=str(user["_id"]),
                message_text=message_text,
            )
            flash("Message sent.", "success")
        return redirect(url_for("chat.chat_thread", chat_id=chat_id))

    return render_template(
        "chat.html",
        chat=chat,
        product=find_product_by_id(chat["product_id"]),
        seller=find_user_by_id(chat["seller_id"]),
    )
