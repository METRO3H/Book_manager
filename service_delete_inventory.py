# Ejemplo de servicio
from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
import json
from datetime import date, datetime
from decimal import Decimal
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def Delete_Book(book_id):
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

        delete_query = f"""
        --sql
        DELETE FROM manga
        WHERE id = %s;
        ;
        """
        


        # Execute the update query
        try:
            cur.execute(delete_query, (book_id,))
            conn.commit()  # Commit the transaction
            cur.close()
            conn.close()
            
            return "Eliminación exitosa!"
        
        except Exception as e:
            print(f"Error during delete: {e}")
            conn.rollback()  # Rollback in case of error
            cur.close()
            conn.close()
            
            return False
        # Close cursor and connection

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

class Delete_Inventory(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        
        if len(request.split(" ")) != 1:
            response = "Error de formato"
            return service_name, response
        
        book_info = Delete_Book(request)
        
        
        if book_info is False:
            response = "Ocurrió un error"
            return service_name, response
        
        
        return service_name, book_info



# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.delete_inventory

test_service = Delete_Inventory(service_name)

test_service.run()
