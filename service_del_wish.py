from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def conectar_bd():
	return psycopg2.connect(
		host=POSTGRES_HOST,
		port=POSTGRES_PORT,
		database=POSTGRES_DB,
		user=POSTGRES_USER,
		password=POSTGRES_PASSWORD
	)

def del_wish_list(manga_name, id_user):
	try:
		conn = conectar_bd()
		cur = conn.cursor()

		# First, get the manga_id from the manga_name
		query_get_manga_id = """
			SELECT id FROM manga
			WHERE title = %s
		"""
		cur.execute(query_get_manga_id, (manga_name,))
		result = cur.fetchone()

		if result is None:
			return f"No se encontró el manga con el nombre: {manga_name}"

		id_manga = result[0]

		# Now, delete the manga from the wishlist
		query_delete = """
			DELETE FROM wishlist
			WHERE user_id = %s AND manga_id = %s
		"""
		values = (id_user, id_manga)
		cur.execute(query_delete, values)

		conn.commit()

		cur.close()
		conn.close()

		return f"El manga: {manga_name} fue eliminado de la lista de deseados."
	
	except Exception as e:
		return f"Ocurrió un error: {str(e)}"

class CustomService(Soa_Service):
	def process_data(self, request):
		global service_name

		response = request.split(" ", 1)
		id_user = response[0]
		manga_name = response[1]

		respuesta = del_wish_list(manga_name, id_user)
		return service_name, respuesta

service_name = service.delete_wish_list
test_service = CustomService(service_name)
test_service.run()