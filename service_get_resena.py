from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime

from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def get_review(manga_id, user_id=None):
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
        
        # Execute SQL query to fetch reviews
        if user_id:
            query = """
                SELECT id, user_id, manga_id, rating, review_text FROM reviews 
                WHERE manga_id = %s AND user_id = %s
            """
            cur.execute(query, (manga_id, user_id))
        else:
            query = """
                SELECT user_id, rating, review_text FROM reviews 
                WHERE manga_id = %s
            """
            cur.execute(query, (manga_id,))

        # Fetch all records
        reviews = []
        for row in cur.fetchall():
            user_id, rating, review_text = row
            reviews.append({
                'user': user_id,
                'rating': rating,
                'review_text': review_text
            })

        # Close cursor and connection
        cur.close()
        conn.close()

        # Convert the list of reviews to a string
        #reviews_str = '\n'.join(map(str, reviews))

        return reviews
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

class CustomService(Soa_Service):

    def process_data(self, request):
        global service_name

        data_parts = request.split('_')

        # if the data is not in the correct format, return an error message
        if len(data_parts) < 1 or len(data_parts) > 2:
            request = "Bad format"
            # request to string
            request = str(request)
            return service_name, request
        #print('paso el if')

        # Assign each part to a variable
        manga_id = data_parts[0]
        user_id = data_parts[1] if len(data_parts) > 1 else None

        # Call the get_reviews function
        answer = get_review(manga_id, user_id)

        response = answer
        
        return service_name, response

# Select the service to use
service_name = service.get_reviews

test_service = CustomService(service_name)

test_service.run()