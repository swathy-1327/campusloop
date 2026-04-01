ALTER TABLE users
    RENAME COLUMN password_hash TO pwd_hash,
    RENAME COLUMN account_status TO acct_stat,
    RENAME COLUMN trust_score TO trust_scr,
    RENAME COLUMN trust_level TO trust_lvl,
    RENAME COLUMN is_verified_seller TO seller_ok;

ALTER TABLE verification_requests
    RENAME COLUMN id_document_ref TO id_ref,
    RENAME COLUMN admin_remark TO admin_note,
    RENAME COLUMN reviewed_by_admin TO admin_id;

ALTER TABLE products
    RENAME COLUMN ai_generated_description TO ai_desc,
    RENAME COLUMN use_type TO use_tag,
    RENAME COLUMN item_condition TO item_cond,
    RENAME COLUMN product_status TO prod_stat,
    RENAME COLUMN removed_by_admin TO admin_rm,
    RENAME COLUMN removal_reason TO rm_note;

ALTER TABLE orders
    RENAME COLUMN payment_method TO pay_mode,
    RENAME COLUMN order_status TO ord_stat;

ALTER TABLE rent_requests
    RENAME COLUMN product_name TO prod_name;

ALTER TABLE unavailable_product_requests
    RENAME COLUMN product_name TO prod_name;

ALTER TABLE messages
    RENAME COLUMN message_text TO msg_text;

ALTER TABLE trust_logs
    RENAME COLUMN score_change TO score_chg,
    RENAME COLUMN action_type TO act_type;

ALTER TABLE reports
    RENAME COLUMN reported_by TO report_by,
    RENAME COLUMN target_type TO target_tp,
    RENAME COLUMN reviewed_by_admin TO admin_id;
