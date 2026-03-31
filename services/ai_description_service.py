def generate_product_description(title, category, condition, mode):
    use_line = "available for temporary campus use" if mode == "rent" else "ready for a new owner"
    return (
        f"{title} in {condition.lower()} condition, listed under {category}. "
        f"This item is {use_line} and is suitable for students looking for affordable, reliable campus essentials."
    )
