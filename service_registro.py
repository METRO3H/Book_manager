from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime

from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def add_user(username, email, password, role):
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
        
        # Get the current timestamp
        created_at = datetime.now()

        queryEmail = "SELECT * FROM users WHERE email = %s"
        value = (email,)

        try:
            cur.execute(queryEmail, value)
            result = cur.fetchone()
            if result:
                return "El correo ya se encuentra en uso"
            else:
                query = """
                    INSERT INTO users (username, email, password, role, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (username, email, password, role, created_at)
                cur.execute(query, values)
                
                # Commit the transaction
                conn.commit()
        
        finally:
            # Close cursor and connection
            cur.close()
            conn.close()

        return "The user: " + username + " was added successfully."
              
    except Exception as e:
        return f"An error occurred: {str(e)}"

class CustomService(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        # Proceso de data de usuario para enviar a add_user
        # Data llega como name_mail_password
        # Split the data by underscore

        data_parts = request.split('_')

        # if the data is not in the correct format, return an error message
        if len(data_parts) != 3:
            request = "Bad format"
            # request to string
            request = str(request)
            return service_name, request

        # Assign each part to a variable
        name, email, password = data_parts

        # Call the add_user function
        answer = add_user(name, email, password, "customer")

        
        
        response = answer
        
        return service_name, response


# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.add_user

test_service = CustomService(service_name)

test_service.run()