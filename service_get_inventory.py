# Ejemplo de servicio
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


def Get_Book(book_id):
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

        # Execute SQL query to search for user
        query = """--sql
         SELECT * FROM manga WHERE id = %s;
        """
        cur.execute(query, (book_id,))

        # Fetch one record
        book_info = cur.fetchone()

        # Close cursor and connection
        cur.close()
        conn.close()
        

        if book_info is None:
            return False
        
        attributes = [desc[0] for desc in cur.description]

        # Formatear el resultado como un diccionario
        book_info = dict(zip(attributes, book_info))
        
        book_info = json.dumps(book_info, indent=2, default=custom_serializer, ensure_ascii=False)

        
        return book_info


    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def Get_All():
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

        # Execute SQL query to select manga names and genres
        query = """--sql
         SELECT id, title, genre FROM manga;
        """
        cur.execute(query)

        # Fetch all records
        manga_info = cur.fetchall()

        # Close cursor and connection
        cur.close()
        conn.close()

        if manga_info is None:
            return False

        # Format the results as 'name_genre'
        manga_info = [f"{id}_{name}_{genre}" for id, name, genre in manga_info]

        # Join the results into a single string, separated by commas
        manga_info_str = ",".join(manga_info)

        return manga_info_str

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

class Get_Inventory(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        
        if len(request.split(" ")) != 1:
            response = "Error de formato"
            return service_name, response
        
        book_info = ""
        
        if request == "all":
            book_info = Get_All()
        else:
            book_info = Get_Book(request)
            print(book_info)
        
        if book_info is False:
            response = "Ocurrió un error"
            return service_name, response
        
        
        return service_name, book_info



# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.get_inventory

test_service = Get_Inventory(service_name)

test_service.run()
