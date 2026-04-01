# CampusLoop

CampusLoop is a Flask + MySQL implementation of a campus circular economy platform where students can buy, sell, rent, and request items inside a moderated campus ecosystem.

## Features

- Student registration and login
- Seller verification requests with admin approval
- Trust score and trust level badges
- Product listings for sale or rent
- Marketplace browse, search, and filters
- Rental requests and unavailable item requests
- Product-linked buyer/seller chat
- Order creation and completion flow
- Admin dashboard for moderation
- AI-ready description generation stub for future extension

## Quick Start

1. Create a MySQL database named `campusloop`.
2. Copy `.env.example` to `.env` and update the connection string.
3. Install dependencies with `pip install -r requirements.txt`.
4. Initialize schema with `mysql -u root -p campusloop < sql/schema.sql`.
5. Run the app with `python run.py`.
6. Open `http://127.0.0.1:5000` and, if no admin exists yet, use the `Create First Admin` button on the home page.

## Run On Another PC

1. Install Python 3.11+.
2. Install MySQL Server and start it locally.
3. Clone the repo and switch to the `mysql-version` branch.
4. Run `pip install -r requirements.txt`.
5. Create the database:

```sql
CREATE DATABASE campusloop;
```

6. Copy `.env.example` to `.env` and set your local MySQL credentials:

```text
SECRET_KEY=change-me
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/campusloop
```

7. Run the app with `python run.py`.

This branch is designed to work with any local MySQL server as long as the `DATABASE_URL` matches that machine's username, password, host, and database name.

## Full Frontend Setup Flow

1. Start the app.
2. Open the home page and click `Create First Admin`.
3. Log in as that admin and use the admin dashboard to approve seller requests, update roles, moderate products, and close requests.
4. Register normal users from the frontend and use `Become Seller`, `Add Product`, `Orders`, `Profile`, and `My Listings` for day-to-day changes.
