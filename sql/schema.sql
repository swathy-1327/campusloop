CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    pwd_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'buyer',
    acct_stat VARCHAR(20) NOT NULL DEFAULT 'active',
    trust_scr INT NOT NULL DEFAULT 20,
    trust_lvl VARCHAR(30) NOT NULL DEFAULT 'New User',
    seller_ok BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    id_type VARCHAR(50) NOT NULL,
    id_ref VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    admin_note TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    reviewed_at DATETIME NULL,
    admin_id INT NULL,
    CONSTRAINT fk_verification_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_verification_admin FOREIGN KEY (admin_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    ai_desc TEXT,
    category VARCHAR(50) NOT NULL,
    use_tag VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    item_cond VARCHAR(50) NOT NULL,
    mode VARCHAR(20) NOT NULL,
    image_url VARCHAR(255),
    prod_stat VARCHAR(20) NOT NULL DEFAULT 'available',
    admin_rm BOOLEAN NOT NULL DEFAULT FALSE,
    rm_note VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_seller FOREIGN KEY (seller_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    buyer_id INT NOT NULL,
    seller_id INT NOT NULL,
    pay_mode VARCHAR(30) NOT NULL,
    ord_stat VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    CONSTRAINT fk_order_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_order_buyer FOREIGN KEY (buyer_id) REFERENCES users(id),
    CONSTRAINT fk_order_seller FOREIGN KEY (seller_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS rent_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    prod_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    duration VARCHAR(100) NOT NULL,
    budget DECIMAL(10,2) NOT NULL,
    note TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_rent_request_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS unavailable_product_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    prod_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    budget DECIMAL(10,2) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_unavailable_request_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS chat_threads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    buyer_id INT NOT NULL,
    seller_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_thread_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT fk_thread_buyer FOREIGN KEY (buyer_id) REFERENCES users(id),
    CONSTRAINT fk_thread_seller FOREIGN KEY (seller_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    thread_id INT NOT NULL,
    sender_id INT NOT NULL,
    msg_text TEXT NOT NULL,
    sent_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_message_thread FOREIGN KEY (thread_id) REFERENCES chat_threads(id),
    CONSTRAINT fk_message_sender FOREIGN KEY (sender_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    from_user_id INT NOT NULL,
    to_user_id INT NOT NULL,
    rating INT NOT NULL,
    comment TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_order FOREIGN KEY (order_id) REFERENCES orders(id),
    CONSTRAINT fk_review_from_user FOREIGN KEY (from_user_id) REFERENCES users(id),
    CONSTRAINT fk_review_to_user FOREIGN KEY (to_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS trust_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    score_chg INT NOT NULL,
    act_type VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_trust_log_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_by INT NOT NULL,
    target_tp VARCHAR(30) NOT NULL,
    target_id INT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    admin_id INT NULL,
    CONSTRAINT fk_report_user FOREIGN KEY (report_by) REFERENCES users(id),
    CONSTRAINT fk_report_admin FOREIGN KEY (admin_id) REFERENCES users(id)
);
