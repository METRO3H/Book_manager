import socket

class Soa_Service:
    def __init__(self, bus_address=('localhost', 5000)):
        self.bus_address = bus_address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(bus_address)
        self.sinit = 1

    def send_message(self, message):
        message_length = f"{len(message):05}".encode('utf-8')
        full_message = message_length + message
        self.sock.sendall(full_message)

    def receive_message(self):
        amount_received = 0
        amount_expected = int(self.sock.recv(5))
        while amount_received < amount_expected:
            data = self.sock.recv(amount_expected - amount_received)
            if not data:
                raise RuntimeError("Socket connection broken")
            amount_received += len(data)
            
        print('[Status] Received {!r}'.format(data.decode('utf-8')))    
        return data

    def process_data(self, data):
        """Override this method in subclasses to process received data"""
        raise NotImplementedError("Subclasses must implement this method")

    def run(self):
        try:
            init_message = b'00010sinitservi'
            print(f'sending {init_message.decode("utf-8")}')
            self.send_message(init_message)
            
            while True:
                print("[Status] Waiting for transaction...")
                data = self.receive_message()
                print(f'[Status] Received {data.decode("utf-8")}')
                
                processed_data = self.process_data(data.decode("utf-8"))
                
                if self.sinit == 1:
                    self.sinit = 0
                else:
                  if processed_data:
                    print(f'[Status] Sending response: {processed_data}')
                    self.send_message(processed_data.encode('utf-8'))
        finally:
            print('closing socket')
            self.sock.close()

