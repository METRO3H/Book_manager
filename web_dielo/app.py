from flask import Flask, request, render_template, redirect, url_for
import socket
import os
import sys

# Añadir el directorio padre al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.color import color
from util.list_of_services import service

app = Flask(__name__)

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
    print("correo:", correo)
    send_message(service_name, input_data)
    response = receive_message()[7:]
    if "success" in response:  # Esta condición depende de tu lógica de autenticación
        return redirect(url_for('home'))  # Redirigir a una página de éxito, por ejemplo, 'dashboard'
    else:
        return render_template('login.html', error="Correo o contraseña incorrecta")

@app.route('/home')
def home():
    return "Bienvenido al panel de control"

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Puedes cambiar 5001 al puerto que prefieras
