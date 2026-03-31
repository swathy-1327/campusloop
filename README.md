# CampusLoop

CampusLoop is a Flask + MongoDB MVP for a campus circular economy platform where students can buy, sell, rent, and request second-hand campus items inside a trusted ecosystem.

## Features

- User registration and login
- Buyer, seller, and admin roles
- Seller verification workflow with admin approval
- Trust score and trust level badges
- Product listing, browsing, and search
- Buy flow with order creation
- Rental requests and unavailable item requests
- Product-linked buyer/seller chat
- Admin dashboard for moderation

## Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Start MongoDB locally.
5. Run `python app.py`.

The first user who registers with `admin@campusloop.local` becomes the admin automatically.

## Demo Seed

If MongoDB is running locally, you can insert demo users and products with:

```bash
python seed_demo.py
```

Seeded logins:

- `admin@campusloop.local` / `admin123`
- `seller@campusloop.local` / `seller123`
- `buyer@campusloop.local` / `buyer123`
