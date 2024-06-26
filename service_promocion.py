from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def promocion(id_manga, duracion):
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

        # Get the current timestamp
        created_at = datetime.now()
        
        # Execute SQL query to update the manga highlight
        query = """
                    UPDATE highlighted_content
                    SET highlight_type = %s, created_at = %s
                    WHERE manga_id = %s
                """
        values = (duracion, created_at, id_manga)
        cur.execute(query, values)
        
        # Commit the transaction
        conn.commit()
        
        # Close cursor and connection
        cur.close()
        conn.close()

        return "El manga: " + id_manga + " ha sido promocionado satisfactoriamente."
    
    except Exception as e:
        return f"A ocurrido un error: {str(e)}"

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