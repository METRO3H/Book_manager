# Ejemplo de servicio
from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
import json
from datetime import date, datetime
from decimal import Decimal
POSTGRES_HOST = "172.17.0.3"  # METER IP DE SU DOCKER CONTAINER
POSTGRES_PORT = "5432"        # PostgreSQL port debería ser este si no lo cambiaron el default
POSTGRES_DB = "manga_db"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "1234"

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

        # Execute SQL query to search for user
        query = """--sql
         SELECT * FROM manga;
        """
        cur.execute(query)

        # Fetch one record
        book_info = cur.fetchall()

        # Close cursor and connection
        cur.close()
        conn.close()

        if book_info is None:
            return False
        
        attributes = [desc[0] for desc in cur.description]

        # Formatear el resultado como un diccionario
        book_info = [dict(zip(attributes, row)) for row in book_info]
        
        book_info_json = json.dumps(book_info, indent=2, default=custom_serializer, ensure_ascii=False)

        # Verificar la longitud del JSON y recortar si es necesario
        while len(book_info_json) > 985:
            # Remover el último objeto de la lista
            book_info.pop()
            # Convertir nuevamente la lista de objetos a una cadena JSON
            book_info_json = json.dumps(book_info, indent=2, default=custom_serializer, ensure_ascii=False)

        return book_info_json


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
        
        
        if book_info is False:
            response = "Ocurrió un error"
            return service_name, response
        
        
        return service_name, book_info



# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.get_inventory

test_service = Get_Inventory(service_name)

test_service.run()
