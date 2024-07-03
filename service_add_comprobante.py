from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def add_comprobante(user_id, total):
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

        # Insert into comprobante
        query = """
                INSERT INTO comprobante (user_id, total, retirado, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """
        cur.execute(query, (user_id, total, False, datetime.now()))
        
        # Fetch the id of the newly inserted comprobante
        comprobante_id = cur.fetchone()[0]
        
        # Commit the transaction
        conn.commit()
        
        # Close cursor and connection
        cur.close()
        conn.close()

        return comprobante_id
    
    except Exception as e:
        return f"Ha ocurrido un error: {str(e)}"

class CustomService(Soa_Service):
    def process_data(self, request):
        # Split the request string into parts
        parts = request.split('_')
        if len(parts) != 2:
            return "Invalid request format. Expected format: userid_total"

        user_id_str, total_str = parts

        # Convert user_id and total to their appropriate types
        try:
            user_id = int(user_id_str)
            total = float(total_str)
        except ValueError:
            return "Invalid user_id or total. User_id must be an integer and total must be a float."

        # Proceed to add comprobante
        respuesta = add_comprobante(user_id, total)

        return service_name, respuesta

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.genera_comprobante  # Asegúrate de haber agregado 'add_comprobante' a tu list_of_services.py
add_comprobante_service = CustomService(service_name)
add_comprobante_service.run()