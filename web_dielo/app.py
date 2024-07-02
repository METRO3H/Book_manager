from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory, jsonify
import socket
import json
import os
import sys
from funciones import extract_manga_names, search_pdfs, convert_pdf_to_image, send_message, receive_message, check_file_inFolder
from decimal import Decimal
import re

# Definir la iniciación para la web
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

@app.route('/logeo')
def logeo():
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
    
    if len(datos) == 2:
        # La lista tiene dos partes
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
    if response == f"The user: {usuario} was added successfully.":
        return render_template('login.html')
    elif response == "El correo ya se encuentra en uso":
        return render_template('register.html', error="El correo ya se encuentra en uso")
    else:
        return render_template('register.html', error="Error al registrar un nuevo usuario")

@app.route('/admin')
def admin():
    #mangas = get_mangas()
    mangastodos = get_mangas_todos()
    return render_template('admin.html', mangas=mangastodos)

@app.route('/home')
def home():
    message = request.args.get('message')
    mangas = get_mangas()
    return render_template('home.html', mangas=mangas, message=message)

@app.route('/catalogo')
def catalogo():
    service_name = "get_i"  # Nombre del servicio para obtener el contenido destacado
    send_message(service_name, "all")
    response = receive_message()[7:]
    mangas = [manga.split('_') for manga in response.split(',')]
    # print info to send to html
    print(mangas)
    return render_template('catalogo.html', mangas=mangas)

@app.route('/buscar-mangas', methods=['POST'])
def buscarmanga():
    keyword = request.form['search']  # Asumiendo que el campo de búsqueda en tu formulario HTML tiene el nombre 'search'
    service_name = "get_i"
    send_message(service_name, "all")
    response = receive_message()[7:]
    mangas = response.split(',')  # Lista de mangas recibida del servicio
    
    # Filtrar mangas que contienen la palabra clave en su nombre
    filtered_mangas = [manga for manga in mangas if keyword.lower() in manga.lower()]
    # arreglar el formato de los mangas ya que solo se envian los nombres y el genero
    filtered_mangas = [manga.split('_') for manga in filtered_mangas]
    print(filtered_mangas)
    return render_template('catalogo.html', mangas=filtered_mangas)

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

    if response:  # Check if response is not empty
        response = response.strip("[]")
        if response:  # Double check if response is not just "[]"
            mangas = [{'name': manga.split(',')[0].strip(" '()"), 'price': float(manga.split(',')[1].strip(" '()"))} for manga in response.split('), (')]
        else:
            mangas = []  # Set mangas to an empty list if response is empty
    else:
        mangas = []  # Set mangas to an empty list if response is empty

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

@app.route('/manga/<ID>')
def manga_page(ID):
    service_name = "get_i"
    send_message(service_name, str(ID))
    response = json.loads(receive_message()[7:])
    
    image_dir = './static/images'
    image_path = os.path.join(image_dir, f"{response['title']}.pdf.png")
    if not os.path.exists(image_path):
        image_path = convert_pdf_to_image(response['path'], image_dir)
    else:
        image_path = f"{response['title']}.pdf.png"
    response['image'] = url_for('static', filename='images/' + image_path)
    
    reviews, average_rating = get_reviews(ID)
    return render_template('manga_page.html', manga_info=response, title=response["title"], reviews=reviews, average_rating=average_rating)

@app.route('/manga/<manga_id>/add_review', methods=['POST'])
def add_review(manga_id):
    service_name = "rev_i"
    rating = request.form['rating']
    review_text = request.form['review_text']
    user_id = request.form['user_id']
    
    # userid_mangaid_rating_reviewtext`
    input_data = f"{user_id}_{manga_id}_{rating}_{review_text}"

    send_message(service_name, input_data)
    response = receive_message()[7:]
    print(response)
    # retorna que renderice el template de reviews.html
    #return render_template('reviews.html')
    return redirect(url_for('manga_page', ID=manga_id))

@app.route('/mangas/<path:filename>')
def serve_manga(filename):
    return send_from_directory('../mangas', filename)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    manga_id = request.form['manga_id']
    manga_title = request.form['manga_title']
    manga_price = request.form['manga_price']
    user_id = session['user_id']
    service_name = "addcr"
    input_data = f"{user_id}_{manga_price}_{manga_title}"
    send_message(service_name, input_data)
    response = receive_message()[7:]
    print(response)
    return redirect(url_for('manga_page', ID=manga_id, message="Manga added to cart"))

@app.route('/carrito')
def carrito():
    service_name = "getcr"
    user_id = session['user_id']
    send_message(service_name, user_id)
    response = receive_message()[7:]
    print(response)
    if response == "[]":
        return render_template('carrito.html', total=0.0, items=[])
    
    # Regex para encontrar elementos de la tupla
    tuple_pattern = re.compile(r"\((\d+), (\d+), Decimal\('([\d.]+)'\), '([^']+)'\)")

    # Convertir cada línea en una tupla
    items = []
    for line in response.split('\n'):
        match = tuple_pattern.match(line)
        if match:
            id = int(match.group(1))
            user_id = int(match.group(2))
            precio = Decimal(match.group(3))
            producto = match.group(4)
            items.append((id, user_id, precio, producto))
    #sumar todos los precios
    total = sum([item[2] for item in items])
    print(items)
    return render_template('carrito.html',items=items, total=total)

@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    manga_id = request.form['manga_id']
    user_id = session['user_id']
    service_name = "addwl"
    input_data = f"{user_id} {manga_id}"
    send_message(service_name, input_data)
    response = receive_message()[7:]
    print(response)
    return redirect(url_for('manga_page', ID=manga_id, message="Manga added to wishlist"))

@app.route('/del_cart_item', methods=['POST'])
def delete_cart_item():
    service_name = "delcr"
    # Ensure there is JSON in the request
    if not request.json or 'itemId' not in request.json:
        return jsonify({'error': 'Bad request'}), 400

    item_id = request.json['itemId']
    send_message(service_name, item_id)
    response = receive_message()[7:]
    print(response)
    
    return jsonify({'message': 'Item deleted successfully'}), 200

@app.route('/add_cart_item', methods=['POST'])
def add_cart_wish():
    service_name = "addcr"
    service_name2 = "getmp"
    
    # Ensure there is JSON in the request
    if not request.json or 'manga_name' not in request.json:
        return jsonify({'error': 'Bad request'}), 400

    manga_name = request.json['manga_name']
    user_id = session['user_id']
    
    send_message(service_name2, manga_name)
    precio = receive_message()[7:]
    print(precio)
    input_data = f"{user_id}_{precio}_{manga_name}"
    send_message(service_name, input_data)
    response = receive_message()[7:]

    print(response)
    return jsonify({'message': 'Item added to cart successfully'}), 200 

@app.route('/del_wish_item', methods=['POST'])
def delete_wish_item():
    service_name = "delwl"
    
    # Ensure there is JSON in the request
    if not request.json or 'manga_name' not in request.json:
        return jsonify({'error': 'Bad request'}), 400

    print('tamo aca concha')
    # hay que enviar el user_id y el manga_id
    manga_name = request.json['manga_name']
    user_id = session['user_id']
    input_data = f"{user_id} {manga_name}"
    send_message(service_name, input_data)

    response = receive_message()[7:]
    print(response)
    
    return jsonify({'message': 'Item deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Bind to all IP addresses
    