from flask import Flask, redirect, url_for, render_template, request
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_service', methods=['POST'])
def register_service():
    email = request.form.get('email')
    password = request.form.get('password')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    sock.connect(bus_address)

    service = 'register'  # replace with your register service name
    data = f'{email},{password}'
    response_length = len(service) + len(data)
    response_length = str(response_length).zfill(5)
    message = response_length + service + data
    message = message.encode('utf-8')

    sock.sendall(message)

    amount_received = 0
    amount_expected = int(sock.recv(5))
    data = ""
    while amount_received < amount_expected:
        data += sock.recv(amount_expected - amount_received).decode('utf-8')
        amount_received = len(data)

    sock.close()

    return data  # you may want to handle the response data here

if __name__ == '__main__':
    app.run(debug=True, port=5001)