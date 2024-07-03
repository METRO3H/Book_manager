from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2

from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def delete_review(review_id):
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
		
		# Execute SQL query to delete review
		query = "DELETE FROM reviews WHERE id = %s"
		cur.execute(query, (review_id,))
		
		# Commit the transaction
		conn.commit()
		
		# Close cursor and connection
		cur.close()
		conn.close()

		return "The review was deleted successfully."
	except Exception as e:
		return f"An error occurred: {str(e)}"

class CustomService(Soa_Service):

	def process_data(self, request):
		global service_name

		# Call the delete_review function
		answer = delete_review(request)

		response = answer
		
		print(response)
		
		return service_name, response

# Select the service to use
service_name = service.del_review

test_service = CustomService(service_name)

test_service.run()