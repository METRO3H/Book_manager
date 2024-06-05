# ------------------------------------------------------------
# Ejemplo de servicio SOA que procesa la transacción recibida
# ------------------------------------------------------------
import socket

class Soa_Service:
    def __init__(self):
        self.bus_address = ('localhost', 5000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.bus_address)
        self.sinit = 1
        message = b'00010sinitservi'
        print ('sending {!r}'.format (message.decode('utf-8')))
        self.sock.sendall (message)
        self.receive_message()

    def run(self):
        try:

            while True:
                request = self.receive_message()[5:]
                response = self.process_data(request)
                self.send_message(response)
                
        finally:
            print ('closing socket')
            self.sock.close ()   
            
    def receive_message(self):
        # Look for the response
        print ("[Status] Waiting for transaction...")
        amount_received = 0
        amount_expected = int(self.sock.recv (5))
        while amount_received < amount_expected:
            data = self.sock.recv (amount_expected - amount_received)
            amount_received += len (data)
        
        data = data.decode('utf-8')
        print('[Status] Received {!r}'.format(data))
        
        return data
        
    def send_message(self, message):
        message = message.encode('utf-8')
        print (' sending {!r}'.format(message))
        self.sock.sendall(message)       
        
    def process_data(self, data):
        """Override this method in subclasses to process received data"""
        raise NotImplementedError("Subclasses must implement this method")


# # Create a TCP/IP socket
# sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
# # Connect the socket to the port where the bus is listening
# bus_address = ('localhost', 5000)
# print ('connecting to {} port {}'.format (*bus_address))
# sock.connect (bus_address)
# try:
#     # Send data
#     message = b'00010sinitservi'
#     print ('sending {!r}'.format (message.decode('utf-8')))
#     sock.sendall (message)
#     sinit = 1
#     while True:
#         # Look for the response
#         print ("[Status] Waiting for transaction...")
#         amount_received = 0
#         amount_expected = int(sock.recv (5))
#         while amount_received < amount_expected:
#             data = sock.recv (amount_expected - amount_received)
#             amount_received += len (data)
            
#         print('[Status] Received {!r}'.format(data.decode('utf-8')))
        
#         if (sinit == 1):
#             sinit = 0
#         else:
#             message = b'00013serviReceived'
#             print (' sending {!r}'.format(message))
#             sock.sendall (message)
# finally:
#     print ('closing socket')
#     sock.close ()


