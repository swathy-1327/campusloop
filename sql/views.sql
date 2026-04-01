CREATE OR REPLACE VIEW users_view AS
SELECT
    id,
    name,
    email,
    phone,
    role,
    acct_stat AS status,
    trust_scr AS score,
    trust_lvl AS level,
    seller_ok AS verified
FROM users;

CREATE OR REPLACE VIEW products_view AS
SELECT
    id,
    seller_id,
    title,
    category,
    use_tag AS use_type,
    price,
    item_cond AS cond,
    mode,
    prod_stat AS status,
    description AS user_desc,
    ai_desc,
    created_at
FROM products;

CREATE OR REPLACE VIEW orders_view AS
SELECT
    id,
    product_id,
    buyer_id,
    seller_id,
    pay_mode AS payment,
    ord_stat AS status,
    created_at
FROM orders;

CREATE OR REPLACE VIEW verify_view AS
SELECT
    id,
    user_id,
    id_type,
    id_ref,
    status,
    admin_id,
    reviewed_at
FROM verification_requests;

CREATE OR REPLACE VIEW rent_view AS
SELECT
    id,
    user_id,
    prod_name,
    category,
    duration,
    budget,
    status,
    created_at
FROM rent_requests;

CREATE OR REPLACE VIEW unavail_view AS
SELECT
    id,
    user_id,
    prod_name,
    category,
    budget,
    status,
    created_at
FROM unavailable_product_requests;

CREATE OR REPLACE VIEW trust_view AS
SELECT
    id,
    user_id,
    reason,
    score_chg AS score_change,
    act_type AS action,
    created_at
FROM trust_logs;
