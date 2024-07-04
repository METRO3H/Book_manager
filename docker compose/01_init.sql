-- init.sql
CREATE DATABASE manga_db;

\connect manga_db;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    blocked BOOLEAN DEFAULT FALSE,
    tries INTEGER DEFAULT 0,
    last_login TIMESTAMP by default NULL
);

CREATE TABLE manga (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(255),
    format VARCHAR(255),
    publication_status VARCHAR(50),
    release_date DATE,
    sales_count INTEGER,
    rental_count INTEGER,
    price DECIMAL(10, 2),
    available_online BOOLEAN,
    physical_copies_available INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rentals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    manga_id INTEGER REFERENCES manga(id),
    rental_date TIMESTAMP,
    return_date TIMESTAMP
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    manga_id INTEGER REFERENCES manga(id),
    sale_date TIMESTAMP,
    quantity INTEGER
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    manga_id INTEGER REFERENCES manga(id),
    rating INTEGER,
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE wishlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    manga_id INTEGER REFERENCES manga(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subject VARCHAR(255),
    message TEXT,
    sent_at TIMESTAMP
);

CREATE TABLE inventory_events (
    id SERIAL PRIMARY KEY,
    manga_id INTEGER REFERENCES manga(id),
    event_type VARCHAR(255),
    event_date TIMESTAMP,
    note TEXT
);

CREATE TABLE highlighted_content (
    id SERIAL PRIMARY KEY,
    manga_id INTEGER REFERENCES manga(id),
    highlight_type VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    price DECIMAL(10, 2),
    manga_name VARCHAR(255)
);

CREATE TABLE comprobante (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total DECIMAL(10, 2),
    retirado BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ventas_mangas_eliminados (
    id SERIAL PRIMARY KEY,
    manga_name VARCHAR(255),
    manga_id INTEGER,
    total DECIMAL(10, 2),
    numero_venta INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
