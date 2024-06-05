# ------------------------------------------------------------
# Ejemplo de servicio SOA que procesa la transacción recibida
# ------------------------------------------------------------
import socket
import sys
# Create a TCP/IP socket
sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the bus is listening
bus_address = ('localhost', 5000)
print ('connecting to {} port {}'.format (*bus_address))
sock.connect (bus_address)
try:
    # Send data
    message = b'00010sinitservi'
    print ('sending {!r}'.format (message.decode('utf-8')))
    sock.sendall (message)
    sinit = 1
    while True:
        # Look for the response
        print ("[Status] Waiting for transaction...")
        amount_received = 0
        amount_expected = int(sock.recv (5))
        while amount_received < amount_expected:
            data = sock.recv (amount_expected - amount_received)
            amount_received += len (data)
            
        print('[Status] Received {!r}'.format(data.decode('utf-8')))
        
        if (sinit == 1):
            sinit = 0
        else:
            message = b'00013serviReceived'
            print (' sending {!r}'.format(message))
            sock.sendall (message)
finally:
    print ('closing socket')
    sock.close ()