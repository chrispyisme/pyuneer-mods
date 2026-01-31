-- ============================================================================
-- SQL Schema and Test Data
-- Created: January 30, 2026
-- Purpose: Test data for Model & Datasource architecture examples
-- ============================================================================

-- Drop existing tables in correct order (respecting foreign keys)
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS=1;

-- Disable foreign key checks during table creation
SET FOREIGN_KEY_CHECKS=0;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(150),
    bio TEXT,
    avatar_url VARCHAR(255),
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_admin BOOLEAN DEFAULT FALSE
);

-- ============================================================================
-- PRODUCTS TABLE
-- ============================================================================
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    sku VARCHAR(100) UNIQUE,
    category VARCHAR(100),
    stock_quantity INT DEFAULT 0,
    status ENUM('active', 'inactive', 'discontinued') DEFAULT 'active',
    featured BOOLEAN DEFAULT FALSE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ============================================================================
-- ORDERS TABLE
-- ============================================================================
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE,
    total_amount DECIMAL(10, 2),
    tax_amount DECIMAL(10, 2),
    shipping_cost DECIMAL(10, 2),
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    shipping_address TEXT,
    billing_address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    shipped_at DATETIME,
    delivered_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ============================================================================
-- ORDER_ITEMS TABLE
-- ============================================================================
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2),
    subtotal DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ============================================================================
-- POSTS TABLE (for blog/content)
-- ============================================================================
CREATE TABLE posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    content LONGTEXT,
    excerpt VARCHAR(500),
    featured_image VARCHAR(255),
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    views INT DEFAULT 0,
    likes INT DEFAULT 0,
    published_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    KEY (status),
    KEY (published_at)
);

-- ============================================================================
-- COMMENTS TABLE
-- ============================================================================
CREATE TABLE comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT NOT NULL,
    user_id INT,
    content TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ============================================================================
-- TEST DATA: USERS
-- ============================================================================
INSERT INTO users (username, email, password_hash, full_name, bio, status, is_admin) VALUES
('alice_smith', 'alice@example.com', '$2y$10$abcdef123456789', 'Alice Smith', 'Software developer and tech enthusiast', 'active', TRUE),
('bob_johnson', 'bob@example.com', '$2y$10$abcdef123456789', 'Bob Johnson', 'Product manager passionate about UX', 'active', FALSE),
('carol_white', 'carol@example.com', '$2y$10$abcdef123456789', 'Carol White', 'Data scientist and analyst', 'active', FALSE),
('david_brown', 'david@example.com', '$2y$10$abcdef123456789', 'David Brown', 'DevOps engineer', 'active', FALSE),
('emma_davis', 'emma@example.com', '$2y$10$abcdef123456789', 'Emma Davis', 'UX/UI Designer', 'active', FALSE),
('frank_miller', 'frank@example.com', '$2y$10$abcdef123456789', 'Frank Miller', 'Backend specialist', 'inactive', FALSE),
('grace_wilson', 'grace@example.com', '$2y$10$abcdef123456789', 'Grace Wilson', 'Full-stack developer', 'active', FALSE),
('henry_moore', 'henry@example.com', '$2y$10$abcdef123456789', 'Henry Moore', 'Project manager', 'banned', FALSE);

-- ============================================================================
-- TEST DATA: PRODUCTS
-- ============================================================================
INSERT INTO products (name, description, price, cost, sku, category, stock_quantity, status, featured, created_by) VALUES
('Laptop Pro 15', 'High-performance laptop with 16GB RAM and 512GB SSD', 1299.99, 800.00, 'LP-15-001', 'Electronics', 25, 'active', TRUE, 1),
('Wireless Mouse', 'Ergonomic wireless mouse with 2.4GHz connection', 29.99, 8.00, 'WM-001', 'Accessories', 150, 'active', FALSE, 1),
('USB-C Hub', 'Multi-port USB-C hub with HDMI and Ethernet', 49.99, 20.00, 'UC-HUB-001', 'Accessories', 80, 'active', TRUE, 1),
('Monitor 27in', '4K IPS monitor with HDR support', 399.99, 200.00, 'MON-27-001', 'Electronics', 15, 'active', FALSE, 1),
('Mechanical Keyboard', 'RGB backlit mechanical keyboard with Cherry MX switches', 149.99, 70.00, 'KB-MX-001', 'Accessories', 45, 'active', TRUE, 1),
('Webcam 4K', 'Ultra HD webcam with autofocus and built-in microphone', 119.99, 50.00, 'WC-4K-001', 'Electronics', 35, 'active', FALSE, 1),
('Desk Lamp LED', 'Smart LED desk lamp with USB charging', 59.99, 25.00, 'DL-LED-001', 'Lighting', 60, 'active', FALSE, 1),
('Phone Stand', 'Adjustable phone/tablet stand for desk', 19.99, 5.00, 'PS-ADJ-001', 'Accessories', 200, 'active', FALSE, 2),
('External SSD 1TB', 'Portable SSD with 1TB capacity and USB-C', 129.99, 60.00, 'SSD-1TB-001', 'Storage', 70, 'active', TRUE, 1),
('Power Strip 6-outlet', 'Smart power strip with surge protection', 39.99, 12.00, 'PS-6OUT-001', 'Power', 120, 'active', FALSE, 1);

-- ============================================================================
-- TEST DATA: ORDERS
-- ============================================================================
INSERT INTO orders (user_id, order_number, total_amount, tax_amount, shipping_cost, status) VALUES
(2, 'ORD-2026-001', 1379.97, 110.40, 10.00, 'delivered'),
(3, 'ORD-2026-002', 99.97, 8.00, 5.00, 'shipped'),
(4, 'ORD-2026-003', 599.99, 48.00, 10.00, 'processing'),
(5, 'ORD-2026-004', 179.98, 14.40, 5.00, 'pending'),
(2, 'ORD-2026-005', 449.97, 36.00, 10.00, 'delivered'),
(6, 'ORD-2026-006', 129.99, 10.40, 0.00, 'shipped'),
(7, 'ORD-2026-007', 299.97, 24.00, 5.00, 'cancelled'),
(3, 'ORD-2026-008', 89.98, 7.20, 5.00, 'pending');

-- ============================================================================
-- TEST DATA: ORDER_ITEMS
-- ============================================================================
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES
(1, 1, 1, 1299.99, 1299.99),
(1, 2, 1, 29.99, 29.99),
(1, 3, 1, 49.99, 49.99),
(2, 6, 1, 119.99, 119.99),
(2, 8, 1, 19.99, 19.99),
(2, 10, 1, 39.99, 39.99),
(3, 4, 1, 399.99, 399.99),
(3, 7, 1, 59.99, 59.99),
(3, 5, 1, 149.99, 149.99),
(4, 9, 1, 129.99, 129.99),
(4, 2, 1, 29.99, 29.99),
(5, 1, 1, 1299.99, 1299.99),
(5, 3, 1, 49.99, 49.99),
(6, 9, 1, 129.99, 129.99),
(7, 4, 1, 399.99, 399.99),
(7, 5, 1, 149.99, 149.99),
(8, 6, 1, 119.99, 119.99),
(8, 8, 1, 19.99, 19.99);

-- ============================================================================
-- TEST DATA: POSTS
-- ============================================================================
INSERT INTO posts (user_id, title, slug, content, excerpt, status, published_at) VALUES
(1, 'Getting Started with Python', 'getting-started-python', 'Python is a versatile programming language...', 'Learn the basics of Python programming', 'published', '2026-01-15 10:00:00'),
(1, 'Advanced Database Design Patterns', 'advanced-database-patterns', 'When designing databases, normalization is key...', 'Explore best practices in database design', 'published', '2026-01-20 14:30:00'),
(3, 'Data Science Trends 2026', 'data-science-trends-2026', 'The field of data science continues to evolve...', 'What\'s new in data science this year', 'published', '2026-01-18 09:15:00'),
(5, 'UI/UX Design Principles', 'uxui-design-principles', 'Creating user-friendly interfaces requires...', 'Essential principles for modern design', 'draft', NULL),
(7, 'DevOps Best Practices', 'devops-best-practices', 'Continuous integration and deployment...', 'Streamline your deployment pipeline', 'published', '2026-01-10 11:00:00'),
(2, 'Product Management Essentials', 'product-management-essentials', 'Being a product manager means...', 'Core skills for product managers', 'draft', NULL);

-- ============================================================================
-- TEST DATA: COMMENTS
-- ============================================================================
INSERT INTO comments (post_id, user_id, content, approved) VALUES
(1, 2, 'Great introduction to Python! Very helpful.', TRUE),
(1, 4, 'Could you elaborate on decorators?', TRUE),
(1, 6, 'This is exactly what I was looking for.', TRUE),
(2, 1, 'Excellent deep dive into normalization.', TRUE),
(2, 5, 'What about denormalization trade-offs?', TRUE),
(3, 2, 'Really insightful analysis of current trends.', TRUE),
(3, 7, 'Looking forward to more data science articles.', TRUE),
(5, 1, 'Would love to see this published soon!', FALSE),
(5, 4, 'This looks great already.', FALSE);

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_created_by ON products(created_by);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_approved ON comments(approved);

-- ============================================================================
-- VIEW: Active Users
-- ============================================================================
CREATE OR REPLACE VIEW active_users AS
SELECT 
    id, 
    username, 
    email, 
    full_name, 
    created_at, 
    is_admin
FROM users 
WHERE status = 'active';

-- ============================================================================
-- VIEW: Popular Products
-- ============================================================================
CREATE OR REPLACE VIEW popular_products AS
SELECT 
    p.id,
    p.name,
    p.price,
    p.category,
    p.stock_quantity,
    COUNT(oi.id) as times_ordered,
    SUM(oi.quantity) as total_units_sold
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
WHERE p.status = 'active'
GROUP BY p.id, p.name, p.price, p.category, p.stock_quantity
ORDER BY times_ordered DESC;

-- ============================================================================
-- VIEW: User Order Summary
-- ============================================================================
CREATE OR REPLACE VIEW user_order_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(o.id) as total_orders,
    SUM(o.total_amount) as total_spent,
    MAX(o.created_at) as last_order_date,
    AVG(o.total_amount) as avg_order_value
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
GROUP BY u.id, u.username, u.email;

-- ============================================================================
-- Sample Queries for Testing
-- ============================================================================

-- Get all active users
-- SELECT * FROM active_users;

-- Get all products in stock
-- SELECT * FROM products WHERE stock_quantity > 0 AND status = 'active';

-- Get orders with items and product details
-- SELECT 
--     o.id, 
--     o.order_number, 
--     u.username, 
--     p.name, 
--     oi.quantity, 
--     oi.unit_price
-- FROM orders o
-- JOIN order_items oi ON o.id = oi.order_id
-- JOIN products p ON oi.product_id = p.id
-- JOIN users u ON o.user_id = u.id
-- ORDER BY o.created_at DESC;

-- Get published posts with comment counts
-- SELECT 
--     p.id,
--     p.title,
--     u.username,
--     p.published_at,
--     COUNT(c.id) as comment_count
-- FROM posts p
-- JOIN users u ON p.user_id = u.id
-- LEFT JOIN comments c ON p.id = c.post_id
-- WHERE p.status = 'published'
-- GROUP BY p.id, p.title, u.username, p.published_at;

-- Get user spending summary
-- SELECT * FROM user_order_summary WHERE total_orders > 0 ORDER BY total_spent DESC;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS=1;
