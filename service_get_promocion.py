from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def get_promocion():
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

        # Execute SQL query to get all the manga highlights
        query = """
                    SELECT m.title, h.highlight_type, h.created_at
                    FROM highlighted_content h
                    JOIN manga m ON h.manga_id = m.id
                """
        cur.execute(query)
        
        # Fetch all the results
        results = cur.fetchall()
        
        # Close cursor and connection
        cur.close()
        conn.close()

        if not results:
            return "No se encontraron promociones."
        else:
            return "\n".join([f"Manga: {manga_title}|Promoción: {highlight_type}" for manga_title, highlight_type, created_at in results])
    
    except Exception as e:
        return f"A ocurrido un error: {str(e)}"

class CustomService(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        request = 'se ha solicitado la promoción de los mangas.'
        respuesta = get_promocion()

        return service_name, respuesta

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.get_contenido_destacado
test_service = CustomService(service_name)
test_service.run()