from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def get_cart_info(user_id):
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

        # Select all items in cart for the given user_id
        query = """
                SELECT * FROM cart WHERE user_id = %s
                """
        cur.execute(query, (user_id,))
        
        # Fetch all rows
        cart_items = cur.fetchall()
        
        # Close cursor and connection
        cur.close()
        conn.close()

        if not cart_items:
            return "No hay items en el carrito para este usuario."

        return cart_items
    
    except Exception as e:
        return f"Ha ocurrido un error: {str(e)}"

class CustomService(Soa_Service):
    def process_data(self, request):
        user_id = request
        cart_info = get_cart_info(user_id)

        return service_name, cart_info

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.get_cart  # Asegúrate de haber agregado 'get_cart' a tu list_of_services.py
get_cart_service = CustomService(service_name)
get_cart_service.run()