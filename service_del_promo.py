from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def eliminar_promocion(id_manga):
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        # Crear un cursor
        cur = conn.cursor()

        # Ejecutar consulta SQL para eliminar el manga de la tabla de promoción
        query = "DELETE FROM highlighted_content WHERE manga_id = %s"
        cur.execute(query, (id_manga,))
        
        # Confirmar la transacción
        conn.commit()
        
        # Cerrar cursor y conexión
        cur.close()
        conn.close()

        return f"El manga con ID {id_manga} ha sido eliminado de la promoción satisfactoriamente."
    
    except Exception as e:
        return f"Ha ocurrido un error: {str(e)}"

class CustomService(Soa_Service):
    def process_data(self, request):
        global service_name
        
        id_manga = request.strip()
        respuesta = eliminar_promocion(id_manga)

        return service_name, respuesta

# Seleccionar el servicio a usar
service_name = service.delpromo
test_service = CustomService(service_name)
test_service.run()