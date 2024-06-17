from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

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
            SELECT id, role FROM users 
            WHERE email = %s AND password = %s
        """
        cur.execute(query, (email, password))

        # Fetch one record
        user = cur.fetchone()

        # Close cursor and connection
        cur.close()
        conn.close()

        # If a user is found, return the id and role, else return False
        if user:
            return user
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
            response = "Bad format"
            return service_name, response

        # Assign each part to a variable
        email, password = data_parts

        # Call the trylog_user function
        user = trylog_user(email, password)
        print(user)
        if user:
            response = f"{user[0]} {user[1]}"
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