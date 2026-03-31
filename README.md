# CampusLoop

CampusLoop is a Flask + MongoDB Atlas MVP for a campus circular economy platform where students can buy, sell, rent, and request second-hand campus items inside a trusted ecosystem.

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
2. Install dependencies with `py -3 -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Create a MongoDB Atlas cluster and copy its connection string.
5. Add the Atlas URI to `.env` as `MONGO_URI`.
6. Keep `ADMIN_EMAIL=admin@gmail.com` in `.env` for the admin account.
7. Run `py -3 app.py`.

Any account registered with `admin@gmail.com` is created as the admin account automatically.

## Demo Seed

If your MongoDB Atlas connection is configured, you can insert demo users and products with:

```bash
py -3 seed_demo.py
```

Seeded logins:

- `admin@gmail.com` / `admin123`
- `seller@campusloop.local` / `seller123`
- `buyer@campusloop.local` / `buyer123`
