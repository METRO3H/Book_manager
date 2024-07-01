
import socket
from util.color import color

#-------------------------------------------
# NO ES NECESARIO TOCAR ESTE CODIGO!!!
#-------------------------------------------
class Soa_Service:
    def __init__(self, service_name):
        self.bus_address = ('localhost', 5000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.bus_address)
        self.sinit = 1
        message = "00010sinit" + service_name
        message = message.encode("utf-8")
        # print ('sending {!r}'.format (message.decode('utf-8')))
        self.sock.sendall (message)
        response = self.receive_message()[5:7]
        if response == "OK":
            print(color("grey", "--------------------------------------------------------------------"))
            print("\033[97;42m Service \033[0m", color("white", "Service"), color("blue",f"{service_name}") ,color("white", "is connected!"))
            return
            
        else:
            print('[Status] The service is not connected!')
            return


    def run(self):
        try:

            while True:
                print(color("grey", "--------------------------------------------------------------------"))

                print(color("magneta", "[Status]"), color("white", "Waiting for transaction.."))
                
                request = self.receive_message()[5:]

                print(color("green", "[Status]"), color("white", "Received"), color("yellow", f"'{request}'"))

                service, data = self.process_data(request)
                self.send_message(service, data)
                
        finally:
            print ('closing socket')
            self.sock.close()   
            
    def receive_message(self):

        amount_received = 0
        amount_expected = int(self.sock.recv (5))
        while amount_received < amount_expected:
            data = self.sock.recv (amount_expected - amount_received)
            amount_received += len (data)
        
        data = data.decode('utf-8')
        
        return data
        
    def send_message(self, service, data):
        response_length = len(str(service)) + len(str(data))
        # print("Size : ", response_length)
        response_length = str(response_length).zfill(5)
        message = response_length + str(service) + str(data)
        message = message.encode('utf-8')
        
        # Lo que realmente se envía
        # print (' sending {!r}'.format(message))
        
        print(color("blue", "[Status]"), color("white", "Sending") , color("yellow",f"'{data}'"))

        
        self.sock.sendall(message)       
        
    def process_data(self, data):
        # Override this method in subclasses to process received data
        raise NotImplementedError("Subclasses must implement this method")


