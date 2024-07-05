from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def promocion(id_manga, duracion):
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

        # Obtener la marca de tiempo actual
        created_at = datetime.now()
        
        # Verificar si el manga ya está en la tabla de promoción
        check_query = "SELECT 1 FROM highlighted_content WHERE manga_id = %s"
        cur.execute(check_query, (id_manga,))
        exists = cur.fetchone()

        if exists:
            # Si el manga ya está en la tabla, actualizar el registro
            update_query = """
                UPDATE highlighted_content
                SET highlight_type = %s, created_at = %s
                WHERE manga_id = %s
            """
            cur.execute(update_query, (duracion, created_at, id_manga))
        else:
            # Si el manga no está en la tabla, insertar un nuevo registro
            insert_query = """
                INSERT INTO highlighted_content (manga_id, highlight_type, created_at)
                VALUES (%s, %s, %s)
            """
            cur.execute(insert_query, (id_manga, duracion, created_at))
        
        # Confirmar la transacción
        conn.commit()
        
        # Cerrar cursor y conexión
        cur.close()
        conn.close()

        return f"El manga con ID {id_manga} ha sido promocionado satisfactoriamente."
    
    except Exception as e:
        return f"Ha ocurrido un error: {str(e)}"

class CustomService(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        
        response = request.split(" ", 1)
        id_manga = response[0]
        duracion = response[1]
        respuesta = promocion(id_manga, duracion)

        return service_name, respuesta

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.contenido_destacado
test_service = CustomService(service_name)
test_service.run()