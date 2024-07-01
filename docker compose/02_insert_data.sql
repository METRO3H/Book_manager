-- insert_data.sql
\c manga_db
-- Insert users
INSERT INTO users (username, email, password, role) VALUES
    ('user1', 'user1@example.com', 'password123', 'customer'),
    ('user2', 'user2@example.com', 'password456', 'customer'),
    ('admin', 'admin@example.com', 'adminpassword', 'admin');

-- Insert manga
INSERT INTO manga (
    title, genre, format, publication_status, release_date, sales_count, rental_count, price, available_online, physical_copies_available
) VALUES
    ('One Piece', 'Adventure', 'Tankōbon', 'Ongoing', '1997-07-22', 450000000, 10000000, 9.99, true, 500),
    ('Naruto', 'Adventure', 'Tankōbon', 'Completed', '1999-09-21', 250000000, 7000000, 10.99, true, 800),
    ('Attack on Titan', 'Action', 'Tankōbon', 'Completed', '2009-09-09', 100000000, 3000000, 11.99, true, 600),
    ('Death Note', 'Thriller', 'Tankōbon', 'Completed', '2003-12-01', 30000000, 1000000, 14.99, true, 550),
    ('Fullmetal Alchemist', 'Fantasy', 'Tankōbon', 'Completed', '2001-07-12', 70000000, 1500000, 13.99, true, 700);

-- Insert rentals
INSERT INTO rentals (user_id, manga_id, rental_date, return_date) VALUES
    (1, 1, '2023-06-01 10:00:00', '2023-06-15 10:00:00'),
    (1, 2, '2023-06-05 14:00:00', '2023-06-20 14:00:00'),
    (2, 3, '2023-06-10 09:00:00', '2023-06-24 09:00:00');

-- Insert sales
INSERT INTO sales (user_id, manga_id, sale_date, quantity) VALUES
    (1, 1, '2023-06-01 12:00:00', 1),
    (2, 4, '2023-06-05 15:00:00', 2),
    (1, 5, '2023-06-10 16:00:00', 1);

-- Insert reviews
INSERT INTO reviews (user_id, manga_id, rating, review_text) VALUES
    (1, 1, 5, 'Amazing story and characters!'),
    (2, 2, 4, 'Great manga, but a bit too long.'),
    (1, 3, 5, 'Incredible plot twists and action scenes.'),
    (2, 4, 4, 'Dark and intriguing storyline.'),
    (1, 5, 5, 'One of the best fantasy mangas I have read.');

-- Insert wishlists
INSERT INTO wishlist (user_id, manga_id) VALUES
    (1, 3),
    (2, 1),
    (2, 5);

-- Insert email notifications
INSERT INTO email_notifications (user_id, subject, message, sent_at) VALUES
    (1, 'Welcome to MangaStore!', 'Thank you for signing up!', '2023-06-01 08:00:00'),
    (2, 'Welcome to MangaStore!', 'Thank you for signing up!', '2023-06-05 08:00:00'),
    (1, 'Your Order Has Shipped', 'Your order of One Piece has shipped.', '2023-06-02 10:00:00');

-- Insert inventory events
INSERT INTO inventory_events (manga_id, event_type, event_date, note) VALUES
    (1, 'Stock Added', '2023-06-01 09:00:00', 'Initial stock added.'),
    (2, 'Stock Added', '2023-06-05 09:00:00', 'Initial stock added.'),
    (3, 'Stock Added', '2023-06-10 09:00:00', 'Initial stock added.');

-- Insert highlighted content
INSERT INTO highlighted_content (manga_id, highlight_type) VALUES
    (1, 'Best Seller'),
    (3, 'Editors Pick'),
    (5, 'Fan Favorite');

INSERT INTO cart (user_id, price, manga_name) VALUES
    (2, 9.99, 'Naruto');
