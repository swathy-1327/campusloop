from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import ChatThread, Message


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/")
@login_required
def inbox():
    threads = ChatThread.query.filter(
        (ChatThread.buyer_id == current_user.id) | (ChatThread.seller_id == current_user.id)
    ).order_by(ChatThread.created_at.desc())
    return render_template("chat/inbox.html", threads=threads)


@chat_bp.route("/<int:thread_id>", methods=["GET", "POST"])
@login_required
def thread_detail(thread_id):
    thread = ChatThread.query.get_or_404(thread_id)
    if current_user.id not in [thread.buyer_id, thread.seller_id]:
        flash("You do not have access to this thread.", "danger")
        return redirect(url_for("chat.inbox"))

    if request.method == "POST":
        message_text = request.form["message_text"].strip()
        if message_text:
            message = Message(
                thread_id=thread.id,
                sender_id=current_user.id,
                message_text=message_text,
            )
            db.session.add(message)
            db.session.commit()
        return redirect(url_for("chat.thread_detail", thread_id=thread.id))

    return render_template("chat/thread.html", thread=thread)
