from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from datetime import datetime, timedelta
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

        # Check if the account is blocked
        query = """
            SELECT blocked, tries, last_login FROM users 
            WHERE email = %s
        """
        cur.execute(query, (email,))
        user_info = cur.fetchone()

        if user_info:
            blocked, tries, last_login = user_info
            if blocked:
                # Check if 30 minutes have passed since the account was blocked
                if datetime.now() - last_login < timedelta(minutes=1):
                    cur.close()
                    conn.close()
                    return "Cuenta bloqueada por 1 minuto debido a exceso de intentos."

                # Unblock the account if 30 minutes have passed
                query = """
                    UPDATE users
                    SET blocked = FALSE, tries = 0
                    WHERE email = %s
                """
                cur.execute(query, (email,))
                conn.commit()

            # Initialize tries if it's None
            if tries is None:
                tries = 0

        # Execute SQL query to search for user
        query = """
            SELECT id, role FROM users 
            WHERE email = %s AND password = %s
        """
        cur.execute(query, (email, password))

        # Fetch one record
        user = cur.fetchone()

        if user:
            # Reset tries and update last_login on successful login
            query = """
                UPDATE users
                SET tries = 0, last_login = %s
                WHERE email = %s
            """
            cur.execute(query, (datetime.now(), email))
            conn.commit()

            # Close cursor and connection
            cur.close()
            conn.close()
            return user
        else:
            # Increment tries and update last_login on failed login
            tries += 1
            query = """
                UPDATE users
                SET tries = %s, last_login = %s
                WHERE email = %s
            """
            cur.execute(query, (tries, datetime.now(), email))
            conn.commit()

            # Block account if tries exceed 3
            if tries >= 3:
                query = """
                    UPDATE users
                    SET blocked = TRUE
                    WHERE email = %s
                """
                cur.execute(query, (email,))
                conn.commit()

            # Close cursor and connection
            cur.close()
            conn.close()
            return "Correo o contraseña incorrecta"

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "No se ha podido iniciar sesión. El usuario no existe."

class CustomService(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        # Proceso de data de usuario para enviar a add_user
        # Data llega como name_mail_password
        # Split the data by underscore

        data_parts = request.split('_', 1)
        # if the data is not in the correct format, return an error message
        if len(data_parts) != 2:
            response = "Bad format"
            return service_name, response

        # Assign each part to a variable
        email, password = data_parts

        # Call the trylog_user function
        user = trylog_user(email, password)
        print(user)

        if isinstance(user, tuple) and len(user) == 2:
            response = f"{user[0]}_{user[1]}"
            print(response)
        else:
            response = user
            print(response)

        return service_name, response

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.log_user
test_service = CustomService(service_name)
test_service.run()
