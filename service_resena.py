from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime

from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def add_review(user_id, manga_id, rating, review_text):
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
        
        # Execute SQL query to add review
        query = """
            INSERT INTO reviews (user_id, manga_id, rating, review_text)
            VALUES (%s, %s, %s, %s)
        """
        values = (user_id, manga_id, rating, review_text)
        cur.execute(query, values)
        
        # Commit the transaction
        conn.commit()
        
        # Close cursor and connection
        cur.close()
        conn.close()

        return "The review was added successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"

class CustomService(Soa_Service):

    def process_data(self, request):
        global service_name

        data_parts = request.split('_')

        # if the data is not in the correct format, return an error message
        if len(data_parts) != 4:
            request = "Bad format"
            # request to string
            request = str(request)
            return service_name, request

        # Assign each part to a variable
        user_id, manga_id, rating, review_text = data_parts

        # Call the add_review function
        answer = add_review(user_id, manga_id, rating, review_text)

        response = answer
        
        return service_name, response

# Select the service to use
service_name = service.hacer_review

test_service = CustomService(service_name)

test_service.run()