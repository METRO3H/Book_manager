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
        smtp.login(remitente, contraseña)
        smtp.sendmail(remitente, destinatario, em.as_string())
        print("Correo enviado")

# Función para obtener el correo de un usuario por ID
def obtener_correo_usuario(usuario_id):
    try:
        with conectar_bd() as conn:
            with conn.cursor() as cur:
                consulta = "SELECT email FROM users WHERE id = %s;"
                cur.execute(consulta, (usuario_id,))
                resultado = cur.fetchone()
                return resultado[0] if resultado else None
    except Exception as e:
        print(f"Error al obtener el correo del usuario: {e}")
        return None

# Clase para el servicio personalizado
class CustomService(Soa_Service):
    def process_data(self, request):
        global service_name
        load_dotenv()

        # Parsear el mensaje
        try:
            _, usuario_id_str, detalles_compra = request.split('?')
            usuario_id = int(usuario_id_str)
            detalles = detalles_compra.split('_')
            monto_gastado = detalles[0]
            mangas_comprados = detalles[1:]
        except ValueError:
            print("Formato de mensaje incorrecto")
            return service_name, "Formato de mensaje incorrecto"

        # Obtener el correo del usuario
        destinatario = obtener_correo_usuario(usuario_id)
        if not destinatario:
            print(f"No se encontró el correo para el usuario con ID {usuario_id}")
            return service_name, "No se encontró el correo del usuario"

        remitente = "correodetareas11.9@gmail.com"
        contraseña = 'otxm trlz hnvd wlxk'
        asunto = "Comprobante de compra"
        cuerpo = f"Hola,\n\nHas realizado una compra por un monto de {monto_gastado}.\n\nMangas comprados:\n" + "\n".join(mangas_comprados) + f"\n\nID del comprobante: {usuario_id}"

        # Enviar el correo
        enviar_correo(remitente, destinatario, asunto, cuerpo, contraseña)

        return service_name, "Correo enviado satisfactoriamente"

# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.post_compra
test_service = CustomService(service_name)
test_service.run()