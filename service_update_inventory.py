# Ejemplo de servicio
from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
import json

POSTGRES_HOST = "172.17.0.3"  # METER IP DE SU DOCKER CONTAINER
POSTGRES_PORT = "5432"        # PostgreSQL port debería ser este si no lo cambiaron el default
POSTGRES_DB = "manga_db"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "1234"


def Update_Book(book_id, book_parameter, value):
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

        update_query = f"""
        --sql
        UPDATE manga
        SET {book_parameter} = %s
        WHERE id = %s;
        ;
        """
        


        # Execute the update query
        try:
            cur.execute(update_query, (value, book_id,))
            conn.commit()  # Commit the transaction
            cur.close()
            conn.close()
            
            return "Actualización exitosa!"
        
        except Exception as e:
            print(f"Error during update: {e}")
            conn.rollback()  # Rollback in case of error
            cur.close()
            conn.close()
            
            return False
        # Close cursor and connection

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

class Update_Inventory(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        
        request = request.split("|")
        book_id, book_parameter, value = request
        
        if len(request) != 3:
            response = "Error de formato"
            return service_name, response
        
        
        response = Update_Book(book_id, book_parameter, value)
        

        if response is False:
            response = "Ocurrió un error"
            return service_name, response
        
        
        return service_name, response



# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.update_inventory

test_service = Update_Inventory(service_name)

test_service.run()
