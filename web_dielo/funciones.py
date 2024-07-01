import os
from pdf2image import convert_from_path
import socket
import sys
# Añadir el directorio padre al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.color import color
from util.list_of_services import service


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

# Configurar el socket y la dirección del bus
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('localhost', 5000)
sock.connect(bus_address)

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