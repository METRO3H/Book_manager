from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def add_to_cart(user_id, price, manga_name):
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

		# First, find the manga_id based on manga_name
		cur.execute("SELECT id FROM manga WHERE title = %s", (manga_name,))
		manga_id = cur.fetchone()
		if manga_id is None:
			return "Manga no encontrado."

		# Insert into cart
		query = """
				INSERT INTO cart (user_id, price, manga_name)
				VALUES (%s, %s, %s)
				"""
		cur.execute(query, (user_id, price, manga_name))
		
		# Commit the transaction
		conn.commit()
		
		# Close cursor and connection
		cur.close()
		conn.close()

		return "Manga agregado al carrito exitosamente."
	
	except Exception as e:
		return f"Ha ocurrido un error: {str(e)}"

class CustomService(Soa_Service):
	def process_data(self, request):
		# Split the request string into parts
		parts = request.split('_')
		if len(parts) != 3:
			return "Invalid request format. Expected format: userid_price_manganame"

		user_id_str, price_str, manga_name = parts

		# Convert user_id and price to their appropriate types
		try:
			user_id = int(user_id_str)
			price = float(price_str)
			manga_name = str(manga_name)
		except ValueError:
			return "Invalid user_id or price. User_id must be an integer and price must be a float."

		# Proceed to add to cart
		respuesta = add_to_cart(user_id, price, manga_name)

		return service_name, respuesta

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.add_cart  # Asegúrate de haber agregado 'add_cart' a tu list_of_services.py
add_cart_service = CustomService(service_name)
add_cart_service.run()