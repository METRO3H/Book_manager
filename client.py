
import socket
import sys
from util.color import color
from util.list_of_services import service
#-------------------------------------------
# NO ES NECESARIO TOCAR ESTE CODIGO!!!
#-------------------------------------------

# Create a TCP/IP socket
sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the bus is listening
bus_address = ('localhost', 5000)

print(color("grey", "--------------------------------------------------------------------"))
print("\033[97;42m Client \033[0m", color("white",'Connecting to'), color("blue", f'{bus_address[0]}:{bus_address[1]}'))

sock.connect (bus_address)

def send_message(service, data):
    global sock
    response_length = len(service) + len(data)
    response_length = str(response_length).zfill(5)
    message = response_length + service + data
    message = message.encode('utf-8')
    # Lo que realmente se envía
    # print (' sending {!r}'.format(message))
    print(color("blue", "[Status]"), color("white", "Sending to service"), color("yellow", f"'{service}'"),"->",color("yellow", f"'{data}'"))

    sock.sendall(message) 
    return

def receive_message():
    global sock
    amount_received = 0
    amount_expected = int(sock.recv (5))
    while amount_received < amount_expected:
        data = sock.recv (amount_expected - amount_received)
        amount_received += len (data)
    
    data = data.decode('utf-8')
    return data

def menu():
    variables = {key: value for key, value in vars(service).items() if not key.startswith('__')}
    keys = variables.keys()
    for i, key in enumerate(keys):
        key = key.replace("_", " ")
        key = key.capitalize()
        print(color("cyan", f"{str(i + 1)}. {key}"))

    print("0. Exit")
    list_of_keys = list(keys)
    option = input(color("magneta", "Seleccione una opción: "))
    try:
        option = int(option)
        if option == 0:
            return False
        elif 0 < option <= len(keys):
            selected_key = list_of_keys[option - 1]
            return {
                    "option_name": selected_key.replace("_", " ").capitalize(),
                    "service": variables[selected_key]
                }
        else:
            print("Opción no válida.")
            return None
    except ValueError:
        print("Por favor, ingrese un número válido.")
        return None


try:
    while True:
        print(color("grey", "--------------------------------------------------------------------"))
        
        option = menu()
        if option is None:
            continue
        
        if option is False:
            break
        
        option_name = option["option_name"]
        service_name = option["service"]

        request = input(color("cyan", f"{option_name} : "))
        
        send_message(service_name, request)
        
        response = receive_message()[7:]

        print(color("green", "[Status]"), color("white", "Response"), color("yellow", f"'{response}'"))
        

finally:
    print ('closing socket')
    sock.close()
    
