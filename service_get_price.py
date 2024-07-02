from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def Get_Price(manga_name):
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

		# Execute SQL query to search for manga price by name
		query = """--sql
		 SELECT price FROM manga WHERE title = %s;
		"""
		cur.execute(query, (manga_name,))

		# Fetch one record
		price_info = cur.fetchone()

		# Close cursor and connection
		cur.close()
		conn.close()

		if price_info is None:
			return False

		# Return the price as a float
		return float(price_info[0])

	except Exception as e:
		print(f"An error occurred: {str(e)}")
		return False

class CustomService(Soa_Service):
	def process_data(self, request):
		global service_name
		
		price_info = Get_Price(request)
		print(price_info)
		if price_info is False:
			response = "Ocurrió un error"
			return service_name, response
		
		return service_name, float(price_info)

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.get_manga_price

test_service = CustomService(service_name)

test_service.run()