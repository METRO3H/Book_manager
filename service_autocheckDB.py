import psycopg2
from psycopg2 import sql
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

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

# Run the function
check_and_fix_database_integrity()