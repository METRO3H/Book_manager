# Ejemplo de meterle info a la DB

import psycopg2
from datetime import datetime

POSTGRES_HOST = "172.17.0.3"  # METER IP DE SU DOCKER CONTAINER
POSTGRES_PORT = "5432"        # PostgreSQL port deberia ser este si no lo cambiaron el default
POSTGRES_DB = "manga_db"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "1234"

def add_user(username, email, password, role):
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    
    # Create a cursor object
    cur = conn.cursor()
    
    # Get the current timestamp
    created_at = datetime.now()
    
    # Execute SQL query to add user
    query = """
        INSERT INTO users (username, email, password, role, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (username, email, password, role, created_at)
    cur.execute(query, values)
    
    # Commit the transaction
    conn.commit()
    
    # Close cursor and connection
    cur.close()
    conn.close()

# Example usage
if __name__ == "__main__":
    # Prompt user for input
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    role = input("Enter role: ")
    
    # Add user to database
    add_user(username, email, password, role)
    
    print("User added successfully.")
