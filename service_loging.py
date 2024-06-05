from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime

POSTGRES_HOST = "172.17.0.3"  # METER IP DE SU DOCKER CONTAINER
POSTGRES_PORT = "5432"        # PostgreSQL port deberia ser este si no lo cambiaron el default
POSTGRES_DB = "manga_db"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "1234"

def trylog_user(email, password):
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

        # Execute SQL query to search for user
        query = """
            SELECT * FROM users 
            WHERE email = %s AND password = %s
        """
        cur.execute(query, (email, password))

        # Fetch one record
        user = cur.fetchone()

        # Close cursor and connection
        cur.close()
        conn.close()

        # If a user is found, return True, else return False
        if user:
            return True
        else:
            return False

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

    
class CustomService(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        # Proceso de data de usuario para enviar a add_user
        # Data llega como name_mail_password
        # Split the data by underscore

        data_parts = request.split('_')
        # if the data is not in the correct format, return an error message
        if len(data_parts) != 2:
            request = "Bad format"
            return service_name, request

        # Assign each part to a variable
        email, password = data_parts

        # Call the add_user function
        answer = trylog_user(email, password)
        print(answer)
        if answer:
            response = "success"
            print(response)
        else:
            response = "error"
            print(response)

        return service_name, response


# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.log_user

test_service = CustomService(service_name)

test_service.run()