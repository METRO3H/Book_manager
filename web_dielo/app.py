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
    variables = {key: value for key, value in vars(service).items() if not key.startswith('__')}
    keys = variables.keys()
    return render_template('index.html', services=keys)

@app.route('/procesar', methods=['POST'])
def procesar():
    selected_service = request.form['service']
    input_data = request.form['input_data']
    service_name = getattr(service, selected_service)

    send_message(service_name, input_data)
    response = receive_message()[7:]
    return render_template('resultado.html', service=selected_service.replace('_', ' ').capitalize(), input_data=input_data, response=response)

if __name__ == '__main__':
    # Cambia el puerto aquí
    app.run(debug=True, port=5001)  # Puedes cambiar 8080 al puerto que prefieras