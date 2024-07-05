import psycopg2
from psycopg2 import sql
from soa_service import Soa_Service
from util.list_of_services import service
from credencialBD import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

def Get_Sales(date, period):
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

        # Split the date into year, month, and day
        year, month, day = map(int, date.split('-'))

        # Construct the SQL query
        if period == 'year':
            # Group by year
            query = """
                SELECT EXTRACT(YEAR FROM sale_date) AS year, SUM(quantity) AS total_quantity, SUM(quantity * m.price) AS total_revenue
                FROM sales s
                JOIN manga m ON s.manga_id = m.id
                WHERE EXTRACT(YEAR FROM sale_date) = %s
                GROUP BY EXTRACT(YEAR FROM sale_date)
                ORDER BY year
            """
            # Execute the query
            cur.execute(query, (year,))
        elif period == 'month':
            # Group by month
            query = """
                SELECT EXTRACT(MONTH FROM sale_date) AS month, SUM(quantity) AS total_quantity, SUM(quantity * m.price) AS total_revenue
                FROM sales s
                JOIN manga m ON s.manga_id = m.id
                WHERE EXTRACT(YEAR FROM sale_date) = %s AND EXTRACT(MONTH FROM sale_date) = %s
                GROUP BY EXTRACT(MONTH FROM sale_date)
                ORDER BY month
            """
            # Execute the query
            cur.execute(query, (year, month))
        elif period == 'day':
            # Group by day
            query = """
                SELECT DATE(sale_date) AS day, SUM(quantity) AS total_quantity, SUM(quantity * m.price) AS total_revenue
                FROM sales s
                JOIN manga m ON s.manga_id = m.id
                WHERE EXTRACT(YEAR FROM sale_date) = %s AND EXTRACT(MONTH FROM sale_date) = %s AND EXTRACT(DAY FROM sale_date) = %s
                GROUP BY DATE(sale_date)
                ORDER BY day
            """
            # Execute the query
            cur.execute(query, (year, month, day))
        elif period == 'deleted':
           # Group by month for deleted manga sales
            query = """
                SELECT SUM(total) AS total_revenue
                FROM ventas_mangas_eliminados
            """
            # Execute the query
            cur.execute(query,)
            total = cur.fetchall()

            # Close cursor and connection
            cur.close()
            conn.close()
            
            return total
        else:
            raise ValueError("Invalid period specified. Supported values are 'day', 'month', or 'year'.")

        # Fetch all rows
        rows = cur.fetchall()

        # Extract only the total_revenue values
        revenues = [row[2] for row in rows]

        # Close cursor and connection
        cur.close()
        conn.close()

        return revenues

    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database or executing query:", e)
        return None

class Get_Sales_Rentals_Service(Soa_Service):
    def process_data(self, request):
        global service_name

        # Split the request into parts
        parts = request.split("_")

        # Divide the period from the date
        period = parts[-1]
        date_str = parts[0]
        # el mensaje se debe ver como "day_2021-01-01"
        fecha = date_str  # Use full date for 'day' period
        
        print(f"Getting sales statistics for {period} {fecha}")
        # Call Get_Sales function
        response = Get_Sales(fecha, period)
        # retornar solo el revenue
        
        return service_name, response

# Set the service name
service_name = service.get_estadisticas

# Create and run the service
test_service = Get_Sales_Rentals_Service(service_name)
test_service.run()


