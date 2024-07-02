import os
from pdf2image import convert_from_path
import socket
import sys
import json
from time import sleep
# Añadir el directorio padre al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.color import color
from util.list_of_services import service

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
