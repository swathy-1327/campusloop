def format_currency(value):
    try:
        return f"Rs. {float(value):,.0f}"
    except (TypeError, ValueError):
        return "Rs. 0"


def format_datetime(value):
    if not value:
        return "-"
    return value.strftime("%d %b %Y, %I:%M %p")


def trust_badge_class(level):
    mapping = {
        "Highly Trusted": "badge-gold",
        "Trusted Seller": "badge-green",
        "Basic Verified": "badge-blue",
        "New User": "badge-gray",
    }
    return mapping.get(level, "badge-gray")
