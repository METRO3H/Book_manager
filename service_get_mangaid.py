from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
import json
from datetime import date, datetime
from decimal import Decimal
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def custom_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def Get_MangaID(manga_name):
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

        # Execute SQL query to search for manga ID by name
        query = """--sql
         SELECT id FROM manga WHERE title = %s;
        """
        cur.execute(query, (manga_name,))

        # Fetch one record
        manga_id = cur.fetchone()

        # Close cursor and connection
        cur.close()
        conn.close()

        if manga_id is None:
            return False

        return manga_id[0]

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

class Get_MangaID_Service(Soa_Service):
    def process_data(self, request):
        global service_name
        
        manga_id = Get_MangaID(request)
        print('se esta buscando el manga id de:', request)
        
        if manga_id is False:
            response = "Manga no encontrado o ocurrió un error"
            return service_name, response
        
        return service_name, str(manga_id)

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.get_mangaid

test_service = Get_MangaID_Service(service_name)

test_service.run()