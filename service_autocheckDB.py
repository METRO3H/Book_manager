import psycopg2
from psycopg2 import sql
import os
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from time import sleep

def check_and_fix_database_integrity():
    print("Starting database integrity check...")
    try:
        # Connect to your PostgreSQL database
        print("Connecting to the database...")
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cursor = conn.cursor()

        # Define checks and fixes
        checks_and_fixes = [
            {
                "name": "Orphan comments",
                "check_query": """
                    SELECT r.id FROM reviews r
                    LEFT JOIN manga m ON r.manga_id = m.id
                    WHERE m.id IS NULL;
                """,
                "fix_query": """
                    DELETE FROM reviews WHERE id = %s;
                """
            },
            {
                "name": "Orphan wishlist items",
                "check_query": """
                    SELECT w.id FROM wishlist w
                    LEFT JOIN manga m ON w.manga_id = m.id
                    WHERE m.id IS NULL;
                """,
                "fix_query": """
                    DELETE FROM wishlist WHERE id = %s;
                """
            },
            {
                "name": "Orphan reviews",
                "check_query": """
                    SELECT r.id FROM reviews r
                    LEFT JOIN users u ON r.user_id = u.id
                    WHERE u.id IS NULL;
                """,
                "fix_query": """
                    DELETE FROM reviews WHERE id = %s;
                """
            },
            {
                "name": "Orphan rentals",
                "check_query": """
                    SELECT r.id FROM rentals r
                    LEFT JOIN manga m ON r.manga_id = m.id
                    WHERE m.id IS NULL;
                """,
                "fix_query": """
                    DELETE FROM rentals WHERE id = %s;
                """
            },
            {
                "name": "Orphan sales",
                "check_query": """
                    SELECT s.id FROM sales s
                    LEFT JOIN manga m ON s.manga_id = m.id
                    WHERE m.id IS NULL;
                """,
                "fix_query": """
                    DELETE FROM sales WHERE id = %s;
                """
            },
            {
                "name": "Orphan email notifications",
                "check_query": """
                    SELECT e.id FROM email_notifications e
                    LEFT JOIN users u ON e.user_id = u.id
                    WHERE u.id IS NULL;
                """,
                "fix_query": """
                    DELETE FROM email_notifications WHERE id = %s;
                """
            },
            {
                "name": "Orphan inventory events",
                "check_query": """
                    SELECT i.id FROM inventory_events i
                    LEFT JOIN manga m ON i.manga_id = m.id
                    WHERE m.id IS NULL;
                """,
                "fix_query": """
                    DELETE FROM inventory_events WHERE id = %s;
                """
            },
            {
                "name": "Orphan highlighted content",
                "check_query": """
                    SELECT h.id FROM highlighted_content h
                    LEFT JOIN manga m ON h.manga_id = m.id
                    WHERE m.id IS NULL;
                """,
                "fix_query": """
                    DELETE FROM highlighted_content WHERE id = %s;
                """
            }
        ]
        
        checks_and_fixes_dupes = [
            {
                "name": "Duplicate reviews",
                "check_query": """
                    SELECT user_id, manga_id, review_text, COUNT(*)
                    FROM reviews
                    GROUP BY user_id, manga_id, review_text
                    HAVING COUNT(*) > 1;
                """,
                "fix_query": """
                    DELETE FROM reviews
                    WHERE id IN (
                        SELECT id
                        FROM (
                            SELECT id, ROW_NUMBER() OVER (partition BY user_id, manga_id, review_text ORDER BY id) AS rnum
                            FROM reviews
                        ) t
                        WHERE t.rnum > 1
                    );
                """
            },
            {
                "name": "Duplicate wishlist items",
                "check_query": """
                    SELECT user_id, manga_id, COUNT(*)
                    FROM wishlist
                    GROUP BY user_id, manga_id
                    HAVING COUNT(*) > 1;
                """,
                "fix_query": """
                    DELETE FROM wishlist
                    WHERE id IN (
                        SELECT id
                        FROM (
                            SELECT id, ROW_NUMBER() OVER (partition BY user_id, manga_id ORDER BY id) AS rnum
                            FROM wishlist
                        ) t
                        WHERE t.rnum > 1
                    );
                """
            }
        ]
        
        # Execute checks and fixes
        print("Executing checks and fixes...")
        for check_and_fix in checks_and_fixes + checks_and_fixes_dupes:
            print(f"Running check: {check_and_fix['name']}...")
            cursor.execute(check_and_fix["check_query"])
            results = cursor.fetchall()
            if results:
                print(f"Issues found for {check_and_fix['name']}: {results}")
                print("Fixing issues...")
                for row in results:
                    cursor.execute(check_and_fix["fix_query"], (row[0],))
                conn.commit()
                print("Issues fixed.")
            else:
                print(f"No issues found for {check_and_fix['name']}.")

        # Close connection
        print("Closing database connection...")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error checking and fixing database integrity: {e}")

    print("Database integrity check completed.")



def check_and_add_mangas():
    print("Starting manga check and add...")
    try:
        # Connect to your PostgreSQL database
        print("Connecting to the database...")
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cursor = conn.cursor()

        # Get list of all manga files in the folder
        manga_folder = "mangas"
        manga_files = os.listdir(manga_folder)
        manga_titles = [os.path.splitext(file)[0] for file in manga_files if file.endswith('.pdf')]

        # Define check and fix queries
        check_query = "SELECT title FROM manga WHERE title = %s;"
        fix_query = """
            INSERT INTO manga (title, genre, format, publication_status, release_date, sales_count, rental_count, price, available_online, physical_copies_available)
            VALUES (%s, 'Miscellaneous', 'PDF', 'Unknown', CURRENT_DATE, 0, 0, 0.00, FALSE, 0);
        """

        # Execute checks and fixes
        print("Executing checks and fixes...")
        for title in manga_titles:
            print(f"Checking if manga '{title}' is in the database...")
            cursor.execute(check_query, (title,))
            result = cursor.fetchone()
            if result is None:
                print(f"Manga '{title}' is not in the database. Adding it...")
                cursor.execute(fix_query, (title,))
                conn.commit()
                print("Manga added.")
            else:
                print(f"Manga '{title}' is already in the database.")

        # Close connection
        print("Closing database connection...")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error checking and adding mangas: {e}")

    print("Manga check and add completed.")

def check_and_delete_orphan_mangas():
    print("Starting orphan manga check and deletion...")
    try:
        # Connect to your PostgreSQL database
        print("Connecting to the database...")
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cursor = conn.cursor()

        # Fetch all manga titles and their IDs from the database
        cursor.execute("SELECT title, id FROM manga;")
        db_manga_titles_ids = cursor.fetchall()

        # Get list of all manga files in the folder
        manga_folder = "mangas"
        manga_files = os.listdir(manga_folder)
        manga_titles = [os.path.splitext(file)[0] for file in manga_files if file.endswith('.pdf')]

        # Check and delete orphan mangas from the database
        for db_title, db_id in db_manga_titles_ids:
            print(f"Checking manga '{db_title}' in the database against the folder...")
            if db_title not in manga_titles:
                print(f"Manga '{db_title}' is in the database but the corresponding file is missing. Deleting...")
                # Delete references in related tables
                cursor.execute("DELETE FROM rentals WHERE manga_id = %s;", (db_id,))
                cursor.execute("DELETE FROM sales WHERE manga_id = %s;", (db_id,))
                cursor.execute("DELETE FROM reviews WHERE manga_id = %s;", (db_id,))
                cursor.execute("DELETE FROM wishlist WHERE manga_id = %s;", (db_id,))
                cursor.execute("DELETE FROM inventory_events WHERE manga_id = %s;", (db_id,))
                cursor.execute("DELETE FROM highlighted_content WHERE manga_id = %s;", (db_id,))
                # Finally, delete the manga from the 'manga' table
                cursor.execute("DELETE FROM manga WHERE id = %s;", (db_id,))
                conn.commit()
                print("Deleted.")

        # Close connection
        print("Closing database connection...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking and deleting orphan mangas: {e}")

    print("Orphan manga check and deletion completed.")

def delete_duplicate_reviews():
    print("Starting duplicate reviews deletion...")
    try:
        # Connect to your PostgreSQL database
        print("Connecting to the database...")
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cursor = conn.cursor()

        # Find duplicate reviews
        cursor.execute("""
            SELECT user_id, manga_id
            FROM reviews
            GROUP BY user_id, manga_id
            HAVING COUNT(id) > 1;
        """)
        duplicates = cursor.fetchall()

        # For each duplicate, delete all but the most recent review
        for user_id, manga_id in duplicates:
            print(f"Deleting duplicates for user {user_id} and manga {manga_id}...")
            cursor.execute("""
                DELETE FROM reviews
                WHERE id IN (
                    SELECT id
                    FROM reviews
                    WHERE user_id = %s AND manga_id = %s
                    ORDER BY created_at ASC
                    LIMIT (SELECT COUNT(*) - 1 FROM reviews WHERE user_id = %s AND manga_id = %s)
                );
            """, (user_id, manga_id, user_id, manga_id))

        # Find duplicate entries in the cart
        cursor.execute("""
            SELECT user_id, manga_name
            FROM cart
            GROUP BY user_id, manga_name
            HAVING COUNT(id) > 1;
        """)
        cart_duplicates = cursor.fetchall()

        # For each duplicate in the cart, delete all but the most recent entry
        for user_id, manga_name in cart_duplicates:
            print(f"Deleting duplicates in cart for user {user_id} and manga {manga_name}...")
            cursor.execute("""
                DELETE FROM cart
                WHERE id IN (
                    SELECT id
                    FROM cart
                    WHERE user_id = %s AND manga_name = %s
                    ORDER BY id ASC
                    LIMIT (SELECT COUNT(*) - 1 FROM cart WHERE user_id = %s AND manga_name = %s)
                );
            """, (user_id, manga_name, user_id, manga_name))

        # Commit changes
        conn.commit()

        # Close connection
        print("Closing database connection...")
        cursor.close()
        conn.close()

        print("Duplicate reviews and cart entries deletion completed.")
    except Exception as e:
        print(f"Error deleting duplicate reviews or cart entries: {e}")


if __name__ == "__main__":
    sleep(3)
    #loop every 5 minutes
    while True:
        
        check_and_fix_database_integrity()
        check_and_add_mangas()
        check_and_delete_orphan_mangas()
        delete_duplicate_reviews()
        sleep(300)