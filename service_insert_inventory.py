# Ejemplo de servicio
from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
import json
import datetime
POSTGRES_HOST = "172.17.0.2"  # METER IP DE SU DOCKER CONTAINER
POSTGRES_PORT = "5432"        # PostgreSQL port debería ser este si no lo cambiaron el default
POSTGRES_DB = "manga_db"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "1234"


def Insert_Book(title, genre, format, publication_status, release_date, sales_count, rental_count, price, available_online, physical_copies_available, created_at):
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
            INSERT INTO manga (
                title, genre, format, publication_status, release_date, sales_count, 
                rental_count, price, available_online, physical_copies_available, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ;
        """
        

        data_to_insert = (
           title, genre, format, publication_status, release_date, sales_count, rental_count, price, available_online, physical_copies_available, created_at,
        )

        # Execute the update query
        try:
            cur.execute(update_query, data_to_insert)
            conn.commit()  # Commit the transaction
            cur.close()
            conn.close()
            
            return "Datos insertados correctamente!"
        
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

class Insert_Inventory(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        
        request = request.split("|")
        title, genre, format, publication_status, release_date, sales_count, rental_count, price, available_online, physical_copies_available, created_at = request
        
        if len(request) != 11:
            response = "Error de formato"
            return service_name, response
        
        
        response = Insert_Book(title, genre, format, publication_status, release_date, sales_count, rental_count, price, available_online, physical_copies_available, created_at)
        

        if response is False:
            response = "Ocurrió un error"
            return service_name, response
        
        
        return service_name, response



# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.insert_inventory

test_service = Insert_Inventory(service_name)

test_service.run()
