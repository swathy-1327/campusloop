from flask import Blueprint, render_template

from app.models import Product, RentRequest, UnavailableProductRequest, User


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    admin_exists = User.query.filter_by(role="admin").first() is not None
    featured_products = (
        Product.query.filter_by(product_status="available", removed_by_admin=False)
        .order_by(Product.created_at.desc())
        .limit(6)
        .all()
    )
    recent_rent_requests = RentRequest.query.order_by(RentRequest.created_at.desc()).limit(4).all()
    recent_unavailable = (
        UnavailableProductRequest.query.order_by(UnavailableProductRequest.created_at.desc()).limit(4).all()
    )
    return render_template(
        "index.html",
        featured_products=featured_products,
        recent_rent_requests=recent_rent_requests,
        recent_unavailable=recent_unavailable,
        admin_exists=admin_exists,
    )
