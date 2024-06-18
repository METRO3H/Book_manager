# Importaciones necesarias
from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from datetime import datetime
import os
import ssl
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Función para conectar a la base de datos
def conectar_bd():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

def enviar_correo(remitente, destinatario, asunto, cuerpo, contraseña):
    em = EmailMessage()
    em["From"] = remitente
    em["To"] = destinatario
    em["Subject"] = asunto
    em.set_content(cuerpo)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(remitente,contraseña)
        smtp.sendmail(remitente,destinatario,em.as_string())
        print("Correo enviado")

# Función para buscar mangas estrenados este mes
def buscar_mangas_mes_actual():
    try:
        with conectar_bd() as conn:
            with conn.cursor() as cur:
                ahora = datetime.now()
                mes_actual = ahora.month
                año_actual = ahora.year

                consulta = """
                    SELECT title FROM manga
                    WHERE EXTRACT(MONTH FROM release_date) = %s
                    AND EXTRACT(YEAR FROM release_date) = %s;
                """
                
                values = (mes_actual, año_actual)
                cur.execute(consulta, values)
                
                mangas = cur.fetchall()

                return [manga[0] for manga in mangas]  # El título del manga está en la primera columna del resultado
        
    except Exception as e:
        print(f"Error al buscar mangas: {e}")
        return []

# Función para buscar mangas destacados este mes
def buscar_mangas_destacados():
    try:
        with conectar_bd() as conn:
            with conn.cursor() as cur:
                ahora = datetime.now()

                consulta = """
                    SELECT manga.title
                    FROM manga
                    INNER JOIN highlighted_content ON manga.id = highlighted_content.manga_id
                    WHERE EXTRACT(MONTH FROM highlighted_content.created_at) = %s
                    AND EXTRACT(YEAR FROM highlighted_content.created_at) = %s;
                """
                
                values = (ahora.month, ahora.year)
                cur.execute(consulta, values)
                
                mangas = cur.fetchall()

                return [manga[0] for manga in mangas]  # El título del manga está en la primera columna del resultado de la consulta
        
    except Exception as e:
        print(f"Error al buscar mangas destacados: {e}")
        return []

# Función para obtener el correo de un usuario por ID
def obtener_correo_usuario(usuario_id):
    try:
        with conectar_bd() as conn:
            with conn.cursor() as cur:
                consulta = "SELECT email FROM users WHERE id = %s;"
                cur.execute(consulta, (usuario_id,))
                resultado = cur.fetchone()
                if resultado:
                    return resultado[0]
                else:
                    return None
    except Exception as e:
        print(f"Error al obtener correo del usuario: {e}")
        return None

# Clase para el servicio personalizado
class CustomService(Soa_Service):
    def process_data(self, request):
        global service_name
        load_dotenv()
        datos = request.split(" ", 1)
        usuario_id = datos[0] 
        asunto = datos[1]  
        destinatario = obtener_correo_usuario(usuario_id)

        if not destinatario:
            print(f"No se encontró el correo para el usuario con ID {usuario_id}")
            return service_name, "No se encontró el correo del usuario"

        remitente = "correodetareas11.9@gmail.com"
        contraseña = "otxm trlz hnvd wlxk"
        cuerpo = ""

        if asunto == "Mangas estrenados este mes": # Asunto 1
            mangas_estrenados = buscar_mangas_mes_actual()
            if mangas_estrenados:
                cuerpo = "Hola,\nEstos son los mangas estrenados este mes:\n" + "\n".join(mangas_estrenados)
            else:
                print("No se encontraron mangas estrenados este mes.")
                return service_name, "No se encontraron mangas estrenados este mes"
        elif asunto == "Mangas que estan en destacados": # Asunto 2
            mangas_destacados = buscar_mangas_destacados()
            if mangas_destacados:
                cuerpo = "Hola,\n\nEstos son los mangas que están en destacados:\n" + "\n".join(mangas_destacados)
            else:
                print("No se encontraron mangas en destacados.")
                return service_name, "No se encontraron mangas en destacados"
        else:
            print(f"Asunto no reconocido: {asunto}")
            return service_name, "Asunto no reconocido"
        
        # Para pruebas usar: 
        # destinatario1 = "correodetareas11.9@gmail.com"
        # Y reemplazar en enviar_correo por destinatario => destinatario1
        # Llamar a la función para enviar correo con OAuth2 y la API de Gmail
        enviar_correo(remitente, destinatario, asunto, cuerpo, contraseña)

        return service_name, "Correo enviado satisfactoriamente"

# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.notification
test_service = CustomService(service_name)
test_service.run()
