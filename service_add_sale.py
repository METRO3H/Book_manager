from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
import json
from datetime import datetime
from decimal import Decimal
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def Add_Sale(user_id, manga_name, quantity):
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

		# Get manga_id from manga_name
		get_manga_id_query = """--sql
		SELECT id FROM manga WHERE title = %s;
		"""
		cur.execute(get_manga_id_query, (manga_name,))
		manga_id = cur.fetchone()[0]

		# Insert sale into sales table
		sale_date = datetime.now()
		insert_sale_query = """--sql
		INSERT INTO sales (user_id, manga_id, sale_date, quantity)
		VALUES (%s, %s, %s, %s)
		RETURNING id;
		"""
		cur.execute(insert_sale_query, (user_id, manga_id, sale_date, quantity))
		sale_id = cur.fetchone()[0]

		# Update sales_count in manga table
		update_manga_query = """--sql
		UPDATE manga
		SET sales_count = sales_count + %s
		WHERE id = %s;
		"""
		cur.execute(update_manga_query, (quantity, manga_id))

		# Commit the transaction
		conn.commit()

		# Close cursor and connection
		cur.close()
		conn.close()

		return sale_id

	except Exception as e:
		print(f"An error occurred: {str(e)}")
		return False

class Add_Sale_Service(Soa_Service):
	def process_data(self, request):
		global service_name
		
		try:
			data = request.split()
			user_id = int(data[0])
			manga_name = " ".join(data[1:])
			quantity = 1  # Assuming quantity is always 1 for simplicity
		except (ValueError, IndexError):
			response = "Error de formato"
			return service_name, response
		
		sale_id = Add_Sale(user_id, manga_name, quantity)
		
		if sale_id is False:
			response = "Ocurrió un error"
			return service_name, response
		
		response = f"Venta agregada con ID: {sale_id}"
		return service_name, response

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.add_sale

test_service = Add_Sale_Service(service_name)

test_service.run()