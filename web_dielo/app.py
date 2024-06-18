from flask import Flask, request, render_template, redirect, url_for, session
import socket
import json
import os
import sys
from pdf2image import convert_from_path
from funciones import extract_manga_names, search_pdfs, convert_pdf_to_image


# Añadir el directorio padre al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.color import color
from util.list_of_services import service

app = Flask(__name__)
# Definir la clave secreta
app.secret_key = 'cotrofroto'

# Configurar el socket y la dirección del bus
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('localhost', 5000)
sock.connect(bus_address)

# directorio de subida de archivos
UPLOAD_FOLDER = '../mangas'
ALLOWED_EXTENSIONS = {'pdf'}  # adjust as needed

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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

    return manga_info  # Return manga_info instead of mangas

# chequear extension archivo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# chequear existencia archivo, si esta, no subir con False
def check_file_inFolder(file):
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename == file.filename:
            return False
    return True

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    correo = request.form['email']
    contraseña = request.form['password']
    input_data = correo + "_" + contraseña
    service_name = "log_i"
    send_message(service_name, input_data)
    response = receive_message()[7:]
    datos = response.split(" ",1)
    user_id = datos[0]
    rol = datos[1]

    if "admin" in rol:
        session['user_id'] = user_id
        session['rol'] = rol
        return redirect(url_for('admin'))
    elif "customer" in rol:
        session['user_id'] = user_id
        session['rol'] = rol
        return redirect(url_for('home'))
    elif "user" in rol:
        session['user_id'] = user_id
        session['rol'] = rol
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Correo o contraseña incorrecta")

@app.route('/registrarse')
def registrarse():
    return render_template('register.html')

@app.route('/registro', methods=['POST'])
def registro():
    usuario = request.form['user']
    correo = request.form['email']
    contraseña = request.form['password']
    input_data = usuario + "_" + correo + "_" + contraseña
    service_name = "reg_i"
    send_message(service_name, input_data)
    response = receive_message()[7:]

    return render_template('login.html')

@app.route('/admin')
def admin():
    #mangas = get_mangas()
    mangastodos = get_mangas_todos()
    return render_template('admin.html', mangas=mangastodos)

@app.route('/home')
def home():
    mangas = get_mangas()
    return render_template('home.html', mangas=mangas)

@app.route('/catalogo')
def catalogo():
    service_name = "get_i"  # Nombre del servicio para obtener el contenido destacado
    send_message(service_name, "all")
    response = receive_message()[7:]
    mangas = [manga.split('_') for manga in response.split(',')]
    return render_template('catalogo.html', mangas=mangas)

@app.route('/buscar-mangas', methods=['POST'])
def buscarmanga():
    service_name = "get_i"  # Nombre del servicio para obtener el contenido destacado
    send_message(service_name, "all")
    response = receive_message()[7:]
    mangas = response.split(',')  # Suponiendo que el contenido destacado se envía como una lista separada por comas
    return render_template('catalogo.html', manga = mangas)

@app.route('/logout')
def logout():
    # Eliminar datos de sesión específicos
    # session.pop('user_id', None)
    # session.pop('rol', None)
    # O limpiar toda la sesión
    session.clear()
    return redirect(url_for('index'))

@app.route('/deseados')
def deseados():
    user_id = session['user_id']  # Get the user id from the session
    service_name = "getwl"  # Nombre del servicio para obtener el contenido destacado
    send_message(service_name, user_id)
    response = receive_message()[7:]
    #si no tiene mangas deseados
    if response == "No hay mangas deseados":
        return render_template('deseados.html', mangas=[])
    # the format is like (manga1,price), (manga2,price), ...
    response = response.strip("[]")
    mangas = [{'name': manga.split(',')[0].strip(" '()"), 'price': float(manga.split(',')[1].strip(" '()"))} for manga in response.split('), (')]
    return render_template('deseados.html', mangas=mangas)

@app.route('/upload', methods=['POST'])
def upload_file():
    service_name = "ins_i"
    genre = request.form['genre']
    file = request.files['file']
    title = file.filename

    if check_file_inFolder(file) and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        input_data = f"VALUES ('{title}', '{genre}', 'PDF', 'Unknown', CURRENT_DATE, 0, 0, 0.00, FALSE, 0);"
        send_message(service_name, input_data)
        return redirect(url_for('admin'))
    
    return redirect(url_for('admin'))

@app.route('/notificar')
def notificar():
    service_name = "notif"
    send_message(service_name, "Mangas que estan en destacados")
    return redirect(url_for('admin'))



@app.route('/manga/<int:ID>')
def manga_page(ID):
    service_name = "get_i"
    send_message(service_name, str(ID))
    response = json.loads(receive_message()[7:])
    print(response)
    # use the manga title to search the image in the directory of static/images and append it to the response
    image_dir = './static/images'
    image_path = os.path.join(image_dir, f"{response['title']}.pdf.png")
    if not os.path.exists(image_path):
        # If the image does not exist, convert the PDF to an image
        image_path = convert_pdf_to_image(response['path'], image_dir)
    else:
        image_path = f"{response['title']}.pdf.png"
    response['image'] = image_path
    return render_template('manga_page.html',manga_info=response, title=response["title"])

from flask import send_from_directory

#here the manga will be sent to the user
@app.route('/mangas/<path:filename>')
def serve_manga(filename):
    return send_from_directory('../mangas', filename)
     

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Puedes cambiar 5001 al puerto que prefieras
    