def guide_user(query):
    normalized = query.lower()
    if "sell" in normalized:
        return "To sell an item, become a verified seller first and then use the Add Product page."
    if "rent" in normalized:
        return "Use the rental request page if you need something temporarily."
    return "CampusLoop helps you buy, sell, rent, and request campus items in one trusted place."
