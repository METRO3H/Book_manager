from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

# Función para conectar a la base de datos
def conectar_bd():
	return psycopg2.connect(
		host=POSTGRES_HOST,
		port=POSTGRES_PORT,
		database=POSTGRES_DB,
		user=POSTGRES_USER,
		password=POSTGRES_PASSWORD
	)

# Clase para el servicio personalizado
class CheckSaleService(Soa_Service):
	def process_data(self, request):
		global service_name
		print('Mensaje llegó como: ', request)
		# Parsear el mensaje
		try:
			user_id_str, comprobante_id_str = request.split('_')
			user_id = int(user_id_str)
			comprobante_id = int(comprobante_id_str)
		except ValueError:
			return service_name, "Formato de mensaje incorrecto"

		try:
			with conectar_bd() as conn:
				with conn.cursor() as cur:
					# Verificar si el comprobante existe
					cur.execute("SELECT user_id, retirado FROM comprobante WHERE id = %s;", (comprobante_id,))
					resultado = cur.fetchone()

					if not resultado:
						return service_name, "error"

					comprobante_user_id, retirado = resultado

					# Verificar si el comprobante pertenece al usuario
					if comprobante_user_id != user_id:
						return service_name, "nopertenece"

					# Verificar si la compra está retirada
					if retirado:
						return service_name, "retirado"

					return service_name, "exito"

		except Exception as e:
			return service_name, f"Ha ocurrido un error: {str(e)}"

# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.check_sale
check_sale_service = CheckSaleService(service_name)
check_sale_service.run()