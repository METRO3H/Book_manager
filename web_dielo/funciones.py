import os
from pdf2image import convert_from_path
import socket
import sys
import json
import zipfile
import datetime
from time import sleep
# Añadir el directorio padre al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.color import color
from util.list_of_services import service
from flask import request, jsonify, session

# directorio de subida de archivos
UPLOAD_FOLDER = '../mangas'
ALLOWED_EXTENSIONS = {'pdf'}  # adjust as needed

# chequear extension archivo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configurar el socket y la dirección del bus
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('localhost', 5000)
sock.connect(bus_address)

def extract_manga_names(response):
    entries = response.split('Manga: ')[1:]
    mangas = []
    for entry in entries:
        name, promo = entry.split('|Promoción: ')
        mangas.append((name.strip(), promo.strip()))
    return mangas

def search_pdfs(manga_name, directory):
    for file in os.listdir(directory):
        if file.endswith('.pdf') and manga_name in file:
            return os.path.join(directory, file)
    return None

def convert_pdf_to_image(pdf_path, output_dir):
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    image_filename = os.path.basename(pdf_path) + '.png'
    image_path = os.path.join(output_dir, image_filename)
    images[0].save(image_path, 'PNG')
    return image_filename  # Return only the filename

# comunicacion con servicios
def send_message(service, data):
    response_length = len(service) + len(data)
    response_length = str(response_length).zfill(5)
    message = response_length + service + data
    message = message.encode('utf-8')
    print(color("blue", "[Status]"), color("white", "Sending to service"), color("yellow", f"'{service}'"), "->", color("yellow", f"'{data}'"))
    sock.sendall(message)

def receive_message():
    amount_received = 0
    amount_expected = int(sock.recv(5))
    data = ""
    while amount_received < amount_expected:
        data = sock.recv(amount_expected - amount_received)
        amount_received += len(data)
    data = data.decode('utf-8')
    return data

# Obtener los mangas de contenido destacado
def get_mangas():
    service_name = "getcd"
    send_message(service_name, "")
    response = receive_message()[7:]

    featured_content = extract_manga_names(response)
    image_dir = './static/images'  # Directory to save images
    os.makedirs(image_dir, exist_ok=True)

    mangas = []
    for name, promo in featured_content:
        pdf_path = search_pdfs(name, '../mangas')
        if pdf_path:
            # Create the image path
            image_path = os.path.join(image_dir, f"{name}.pdf.png")
            # Check if the image already exists
            if not os.path.exists(image_path):
                # If the image does not exist, convert the PDF to an image
                image_path = convert_pdf_to_image(pdf_path, image_dir)
            else:
                image_path = f"{name}.pdf.png"
            mangas.append({'name': name, 'promo': promo, 'image': image_path})
    return mangas

# Obtener todos los mangas
def get_mangas_todos():
    service_name = "get_i"
    send_message(service_name, "all")
    response = receive_message()[7:]
    mangas = [manga.split('_') for manga in response.split(',')]
    mangas_names = [manga[1] for manga in mangas]
    mangas_id = [manga[0] for manga in mangas]
    print(mangas_names)
    
    # search the images of the mangas titles in the directory or create them if they don't exist
    image_dir = './static/images'  # Directory to save images
    os.makedirs(image_dir, exist_ok=True)
    manga_info = []  # New list for storing dictionaries
    for manga_name in mangas_names:
        pdf_path = search_pdfs(manga_name, '../mangas')
        if pdf_path:
            # Create the image path
            image_path = os.path.join(image_dir, f"{manga_name}.pdf.png")
            # Check if the image already exists
            if not os.path.exists(image_path):
                # If the image does not exist, convert the PDF to an image
                image_path = convert_pdf_to_image(pdf_path, image_dir)
            else:
                image_path = f"{manga_name}.pdf.png"
                
            manga_info.append({'name': manga_name, 'image': image_path})  # Append to manga_info instead of mangas
    
    responses = []

    # Recorrer los IDs de los mangas y obtener las respuestas
    for manga_id in mangas_id:
        send_message(service_name, manga_id)
        response = receive_message()[7:]
        responses.append(json.loads(response))

    # Encontrar el manga con el mayor número de ventas
    most_sold_manga = max(responses, key=lambda x: x['sales_count'])
    #sacar el tittle del manga mas vendido
    most_sold_manga = most_sold_manga['title']
        

    return manga_info, most_sold_manga  # Return manga_info instead of mangas

def parse_response(response):
    manga_counts = {}
    for line in response.split('\n'):
        if line.strip():
            parts = line.split(',')
            manga_name = parts[-1].strip().strip("'")
            if manga_name in manga_counts:
                manga_counts[manga_name] += 1
            else:
                manga_counts[manga_name] = 1
    return manga_counts

def add_sales(user_id, response):
    service_name = "addsl"
    mangas = {}
    i = 0
    for line in response.split('\n'):
        if line.strip():
            parts = line.split(',')
            manga_name = parts[-1].strip().strip("'")[:-2]
            mangas[i] = [manga_name]
            i += 1
            input_data = f"{user_id} {manga_name}"
            send_message(service_name, input_data)
            response_addsales = receive_message()[7:]
            print('Se agrega una venta')
            print(response_addsales)
    return mangas

def create_zip_file(mangas, comprobanteid):
    # Define the directory where the ZIP file will be saved
    output_dir = '../mangas_enviados'
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Create the ZIP filename
    zip_filename = os.path.join(output_dir, f"mangas_{comprobanteid}.zip")

    # Create the ZIP file
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for i, manga in mangas.items():
            filename = manga[0] + ".pdf"
            zipf.write(os.path.join('../mangas', filename), filename)
    
    return zip_filename

def gastotalcarro():
    service_name = "getcr"
    user_id = session['user_id']
    send_message(service_name, user_id)
    response = receive_message()[7:]
    print("Response:", response)
    
    total = 0
    
    response = response.split('\n')
    for line in response:
        if line.strip():
            parts = line.split(',')
            total += float(parts[2].strip().strip("'").strip("Decimal('").strip("')"))
    #imprime cada linea de la respuesta que se separo
    for line in response:
        print('esta es la linea:', line)
    return total

def delete_cart_items(response):
    service_name = "delcr"
    for line in response.split('\n'):
        if line.strip():
            parts = line.split(',')
            item_id = parts[0].strip().strip("(")
            send_message(service_name, item_id)
            response = receive_message()[7:]
            print(response)

def get_id_comprobante():
    service_name = "getid"
    send_message(service_name, "")
    response = receive_message()[7:]
    return response

def get_sales():
    service_name = "getes"
    periods = ['day', 'month', 'year']
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    ventas = {}
    for period in periods:
        message = f"{current_date}_{period}"
        send_message(service_name, message)
        response = receive_message()[7:]
        # quitarle el formato [Decimal('123.45')] a 123.45
        response = response.strip("[]").strip("Decimal(')").strip("')")
        print(response)
        ventas[period] = response

    return ventas

def userid_to_username(user_id):
    service_name = "getus"
    send_message(service_name, user_id)
    username = receive_message()[7:]
    return username

def get_reviews(manga_id):
    service_name = "res_i"
    send_message(service_name, manga_id)
    reviews = receive_message()[7:]
    
    if reviews == "[]":
        return [], 0.0  # Devuelve una lista vacía y un promedio de 0.0 si no hay reseñas
    
    reviews = reviews.split('}, {')
    reviews = [review.strip('[]{}') for review in reviews]
    total_rating = 0
    
    parsed_reviews = []
    for review in reviews:
        parts = review.split(', ')
        user_id = parts[0].split(': ')[1]
        rating = int(parts[1].split(': ')[1])  # Asegúrate de convertir el rating a entero
        review_text = parts[2].split(': ')[1].strip("'\"")
        username = userid_to_username(user_id)
        
        parsed_reviews.append({
            'user': username,
            'rating': rating,
            'review_text': review_text
        })
        
        total_rating += rating
    
    average_rating = total_rating / len(parsed_reviews)
    return parsed_reviews, average_rating

def genera_comprobante(gasto):
    service_name = "genco"
    user_id = session['user_id']
    input_data = f"{user_id}_{gasto}"
    send_message(service_name, input_data)
    response = receive_message()[7:]
    return response
    