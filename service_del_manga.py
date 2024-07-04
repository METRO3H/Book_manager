from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
import os
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

# Función para eliminar un manga y todas sus referencias
def eliminar_manga(manga_id):
    try:
        with conectar_bd() as conn:
            with conn.cursor() as cur:
                # Obtener información del manga
                cur.execute("SELECT title, price, sales_count FROM manga WHERE id = %s;", (manga_id,))
                manga = cur.fetchone()
                if not manga:
                    print(f"No se encontró el manga con ID {manga_id}")
                    return "No se encontró el manga"

                manga_name, price, sales_count = manga

                # Eliminar referencias en otras tablas
                cur.execute("DELETE FROM rentals WHERE manga_id = %s;", (manga_id,))
                cur.execute("DELETE FROM sales WHERE manga_id = %s;", (manga_id,))
                cur.execute("DELETE FROM reviews WHERE manga_id = %s;", (manga_id,))
                cur.execute("DELETE FROM wishlist WHERE manga_id = %s;", (manga_id,))
                cur.execute("DELETE FROM inventory_events WHERE manga_id = %s;", (manga_id,))
                cur.execute("DELETE FROM highlighted_content WHERE manga_id = %s;", (manga_id,))
                cur.execute("DELETE FROM cart WHERE manga_name = %s;", (manga_name,))

                # Eliminar el manga de la tabla manga
                cur.execute("DELETE FROM manga WHERE id = %s;", (manga_id,))

                # Registrar la eliminación en ventas_mangas_eliminados
                total = price * sales_count
                cur.execute(
                    "INSERT INTO ventas_mangas_eliminados (manga_name, manga_id, total, numero_venta) VALUES (%s, %s, %s, %s);",
                    (manga_name, manga_id, total, sales_count)
                )

                # Confirmar los cambios
                conn.commit()

                # Eliminar el archivo PDF del manga
                pdf_path = os.path.join('./mangas', f"{manga_name}.pdf")
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    print(f"Archivo {pdf_path} eliminado")
                else:
                    print(f"Archivo {pdf_path} no encontrado")

                return "Manga y todas sus referencias eliminadas correctamente"
    except Exception as e:
        print(f"Error al eliminar el manga: {e}")
        return "Error al eliminar el manga"

# Clase para el servicio personalizado
class CustomService(Soa_Service):
    def process_data(self, request):
        global service_name
        load_dotenv()

        # Parsear el mensaje
        try:
            manga_id_str = request.split('?')[0]
            manga_id = int(manga_id_str)
        except ValueError:
            print("Formato de mensaje incorrecto")
            return service_name, "Formato de mensaje incorrecto"

        # Eliminar el manga y sus referencias
        resultado = eliminar_manga(manga_id)
        return service_name, resultado

# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.delmanga
test_service = CustomService(service_name)
test_service.run()