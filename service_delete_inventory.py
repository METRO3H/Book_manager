# Ejemplo de servicio
from soa_service import Soa_Service
from util.list_of_services import service
import psycopg2
import json
from datetime import date, datetime
from decimal import Decimal
import os
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def Delete_Book(book_id):
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

        # Fetch manga details for logging
        cur.execute("SELECT title, price, sales_count FROM manga WHERE id = %s;", (book_id,))
        manga = cur.fetchone()
        if not manga:
            return "Manga no encontrado"

        manga_title, manga_price, manga_sales_count = manga

        # Insert into ventas_mangas_eliminados
        insert_query = """
        INSERT INTO ventas_mangas_eliminados (manga_name, manga_id, total, numero_venta, created_at)
        VALUES (%s, %s, %s, %s, %s);
        """
        cur.execute(insert_query, (manga_title, book_id, manga_price, manga_sales_count, datetime.now()))

        # Delete references from other tables
        tables = ["rentals", "sales", "reviews", "wishlist", "inventory_events", "highlighted_content"]
        for table in tables:
            cur.execute(f"DELETE FROM {table} WHERE manga_id = %s;", (book_id,))

        # Delete from manga table
        delete_query = "DELETE FROM manga WHERE id = %s;"
        cur.execute(delete_query, (book_id,))

        conn.commit()  # Commit the transaction
        cur.close()
        conn.close()

        # Delete the PDF file
        pdf_path = f"./mangas/{manga_title}.pdf"
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        return "Eliminación exitosa!"
    
    except Exception as e:
        print(f"Error during delete: {e}")
        conn.rollback()  # Rollback in case of error
        cur.close()
        conn.close()
        
        return False

class Delete_Inventory(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        
        if len(request.split(" ")) != 1:
            response = "Error de formato"
            return service_name, response
        
        book_info = Delete_Book(request)
        
        if book_info is False:
            response = "Ocurrió un error"
            return service_name, response
        
        return service_name, book_info

# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.delmanga

test_service = Delete_Inventory(service_name)

test_service.run()