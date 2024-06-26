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

def get_wish_list(user_id):
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        
        query = """
                    SELECT m.title, m.price
                    FROM wishlist w
                    JOIN manga m ON w.manga_id = m.id
                    WHERE w.user_id = %s
                """
        values = (user_id,)
        cur.execute(query, values)
        mangas = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [(manga[0], float(manga[1])) for manga in mangas]
    except Exception as e:
        return [], f"Ocurrió un error al obtener la lista de deseos: {str(e)}"

class CustomService(Soa_Service):
    def process_data(self, request):
        global service_name
        id_user = request
        respuesta = get_wish_list(id_user)
        return service_name, respuesta

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.get_wish_list
test_service = CustomService(service_name)
test_service.run()