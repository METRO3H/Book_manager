from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime

from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def get_user_name(user_id):
    try:
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
        
        # Execute SQL query to fetch user name
        query = """
            SELECT username FROM users 
            WHERE id = %s
        """
        cur.execute(query, (user_id,))

        # Fetch the user name
        row = cur.fetchone()
        user_name = row[0] if row else "User not found"

        # Close cursor and connection
        cur.close()
        conn.close()

        return user_name
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

class CustomService(Soa_Service):

    def process_data(self, request):
        global service_name

        data_parts = request.split('_')
        print(data_parts)
        # if the data is not in the correct format, return an error message
        if len(data_parts) != 1:
            request = "Bad format"
            # request to string
            request = str(request)
            return service_name, request

        # Assign each part to a variable
        user_id = data_parts[0]

        # Call the get_user_name function
        answer = get_user_name(user_id)

        response = answer
        
        return service_name, response

# Select the service to use
service_name = service.get_user

test_service = CustomService(service_name)

test_service.run()