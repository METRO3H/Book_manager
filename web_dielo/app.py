from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory, jsonify, send_file
import zipfile
import socket
import json
import os
import sys
from funciones import extract_manga_names, search_pdfs, convert_pdf_to_image, send_message, receive_message, get_mangas, get_mangas_todos, allowed_file
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

import datetime

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
get_sales()

@app.route('/admin')
def admin():
    mangastodos, most_sold = get_mangas_todos()
    ventas = get_sales()
    print(ventas)
    return render_template('admin.html', mangas=mangastodos, most_sold=most_sold, ventas=ventas)


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
    filtered_mangas = []
    for manga in mangas:
        print(manga)
        partes = manga.split('_')
        titulo = partes[1]
        if keyword.lower() in titulo.lower():
            filtered_mangas.append(partes)
            print(filtered_mangas)
        
    return render_template('catalogo.html', mangas=filtered_mangas)

@app.route('/logout')
def logout():
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
    response = receive_message()[7:]
    print(response)
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

    # hay que enviar el user_id y el manga_id
    manga_name = request.json['manga_name']
    user_id = session['user_id']
    input_data = f"{user_id} {manga_name}"
    send_message(service_name, input_data)

    response = receive_message()[7:]
    print(response)
    
    return jsonify({'message': 'Item deleted successfully'}), 200

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

def delete_cart_items(response):
    service_name = "delcr"
    for line in response.split('\n'):
        if line.strip():
            parts = line.split(',')
            item_id = parts[0].strip().strip("(")
            send_message(service_name, item_id)
            response = receive_message()[7:]
            print(response)

def create_zip_file(mangas):
    zip_filename = "mangas.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for i, manga in mangas.items():
            filename = manga[0] + ".pdf"
            zipf.write(os.path.join('../mangas', filename), filename)
    return zip_filename

@app.route('/checkout', methods=['POST'])
def checkout():
    service_name = "getcr"
    user_id = session['user_id']
    send_message(service_name, user_id)
    response = receive_message()[7:]

    # Parsear el response y contar las ocurrencias de cada manga
    manga_counts = parse_response(response)

    # Verificar si algún manga se repite más de dos veces
    for manga, count in manga_counts.items():
        if count > 2:
            return redirect(url_for('home', message="No puedes comprar más de dos copias de un manga"))

    # Agregar a las ventas
    mangas = add_sales(user_id, response)

    # Eliminar artículos del carrito
    delete_cart_items(response)

    # Crear archivo ZIP con todos los mangas
    zip_filename = create_zip_file(mangas)

    # Enviar el archivo ZIP
    return send_file(zip_filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Bind to all IP addresses
    