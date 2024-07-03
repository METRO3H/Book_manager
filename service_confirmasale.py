from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def confirm_sale(user_id, sales_number):
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

        # Check if the sale exists and its current status
        query = """
                SELECT retirado FROM comprobante
                WHERE user_id = %s AND id = %s
                """
        cur.execute(query, (user_id, sales_number))
        result = cur.fetchone()

        if result is None:
            cur.close()
            conn.close()
            return "Comprobante no encontrado"

        if result[0]:  # If 'retiro' is True
            cur.close()
            conn.close()
            return "No se puede confirmar, ya retirado"

        # Update the 'retiro' status to True
        update_query = """
                       UPDATE comprobante
                       SET retirado = %s
                       WHERE user_id = %s AND id = %s
                       """
        cur.execute(update_query, (True, user_id, sales_number))
        
        # Commit the transaction
        conn.commit()
        
        # Close cursor and connection
        cur.close()
        conn.close()

        return "Compra retirada"
    
    except Exception as e:
        return f"Ha ocurrido un error: {str(e)}"

class ConfirmSaleService(Soa_Service):
    def process_data(self, request):
        # Split the request string into parts
        parts = request.split('_')
        if len(parts) != 2:
            return "Invalid request format. Expected format: userid_salesnumber"

        user_id_str, sales_number_str = parts

        # Convert user_id and sales_number to their appropriate types
        try:
            user_id = int(user_id_str)
            sales_number = int(sales_number_str)
        except ValueError:
            return "Invalid user_id or sales_number. Both must be integers."

        # Proceed to confirm sale
        respuesta = confirm_sale(user_id, sales_number)

        return service_name, respuesta

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.confirm_sale  # Asegúrate de haber agregado 'confirm_sale' a tu list_of_services.py
confirm_sale_service = ConfirmSaleService(service_name)
confirm_sale_service.run()