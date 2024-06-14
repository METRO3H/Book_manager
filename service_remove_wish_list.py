from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def conectar_bd():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

def remove_wish_list(id_manga, id_user):
    try:
        conn = conectar_bd()
        # Create a cursor object
        cur = conn.cursor()

        # Execute SQL query to insert the product into the wish list
        query = """
                    DELETE FROM wishlist 
                    WHERE user_id = %s AND manga_id = %s 
                """
        values = (id_user, id_manga)
        cur.execute(query, values)

        # Commit the transaction
        conn.commit()
        
        # Close cursor and connection
        cur.close()
        conn.close()

        return "El manga: " + id_manga + " fue eliminado de la lista de deseados."
    
    except Exception as e:
        return f"A ocurrido un error: {str(e)}"    
    
class CustomService(Soa_Service):
    def process_data(self, request):
        global service_name

        response = request.split(" ", 1)
        id_user = response[0]
        id_manga = response[1]

        respuesta = remove_wish_list(id_manga, id_user)
        return service_name, respuesta

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.remove_wish_list
test_service = CustomService(service_name)
test_service.run()