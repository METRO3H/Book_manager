from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def delete_from_cart(item_id):
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

		# Delete the item from cart
		cur.execute("DELETE FROM cart WHERE id = %s", (item_id,))

		# Commit the transaction
		conn.commit()

		# Check if the delete was successful
		if cur.rowcount == 0:
			return "Ítem no encontrado o ya fue eliminado."

		# Close cursor and connection
		cur.close()
		conn.close()

		return "Ítem eliminado del carrito exitosamente."
	
	except Exception as e:
		return f"Ha ocurrido un error: {str(e)}"

class CustomService(Soa_Service):
	def process_data(self, request):
		# The request is expected to be just the item_id
		try:
			item_id = int(request)
		except ValueError:
			return "Invalid item_id. Item_id must be an integer."

		# Proceed to delete from cart
		respuesta = delete_from_cart(item_id)

		return service_name, respuesta

# Asegúrate de haber agregado 'delete_cart' a tu list_of_services.py
service_name = service.delete_cart  # Este es el nombre del servicio que debes agregar a list_of_services.py
delete_cart_service = CustomService(service_name)
delete_cart_service.run()