# Ejemplo de servicio
import json
import psycopg2
from soa_service import Soa_Service
from util.list_of_services import service
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

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
         SELECT id, user_id, total FROM comprobante;
        """
        cur.execute(query)

        # Fetch all records
        sells_info = cur.fetchall()

        # Close cursor and connection
        cur.close()
        conn.close()

        if sells_info is None:
            return False

        # Format the results as 'name_genre'
        sells_info = [f"{id}_{user_id}_{total}" for id, user_id, total in sells_info]

        # Join the results into a single string, separated by commas
        sells_info_str = ",".join(sells_info)
        
        
        return sells_info_str

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False



class CustomService(Soa_Service):
    
    def process_data(self, request):
        global service_name
        
        response = Get_All()
        
        return service_name, str(response)




service_name = service.show_sales

test_service = CustomService(service_name)

test_service.run()