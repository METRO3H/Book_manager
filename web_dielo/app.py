from flask import Flask, request, render_template, redirect, url_for, session
import socket
import os
import sys

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

    if "admin" in response:
        session['user_id'] = user_id
        session['rol'] = rol
        return redirect(url_for('admin'))
    elif "customer" in response:
        session['user_id'] = user_id
        session['rol'] = rol
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Correo o contraseña incorrecta")

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/home')
def home():
    service_name = "getcd"  # Nombre del servicio para obtener el contenido destacado
    send_message(service_name, "")
    response = receive_message()[7:]
    featured_content = response.split(',')  # Suponiendo que el contenido destacado se envía como una lista separada por comas
    return render_template('home.html', featured_content = featured_content)

@app.route('/catalogo')
def catalogo():
    service_name = "get_i"  # Nombre del servicio para obtener el contenido destacado
    send_message(service_name, "all")
    response = receive_message()[7:]
    mangas = response.split(',')  # Suponiendo que el contenido destacado se envía como una lista separada por comas
    return render_template('catalogo.html', mangas = mangas)

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Puedes cambiar 5001 al puerto que prefieras
