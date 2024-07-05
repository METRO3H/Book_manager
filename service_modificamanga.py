import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from soa_service import Soa_Service
from util.list_of_services import service


def update_manga(manga_id, title, genre, status, price):
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

        # Execute SQL query to update manga
        query = """--sql
         UPDATE manga SET title = %s, genre = %s, publication_status = %s, price = %s WHERE id = %s;
        """
        cur.execute(query, (title, genre, status, price, manga_id))

        # Commit the transaction
        conn.commit()

        # Close cursor and connection
        cur.close()
        conn.close()

        return "Manga updated successfully"

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "Internal server error"
    

class Mod_Inventory(Soa_Service):
    def process_data(self, request):
        global service_name
        
        print("Request:", request)
        data = request.split("_")
        if len(data) != 5:
            response = "Error de formato"
            return service_name, response
        
        manga_id, title, genre, status, price = data
        
        response = update_manga(manga_id, title, genre, status, price)
        return service_name, response

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.mod_inventory
test_service = Mod_Inventory(service_name)
test_service.run()