# Ejemplo de servicio
from soa_service import Soa_Service
from util.list_of_services import service

class CustomService(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        
        response = "XDDDDDD" + request + "XDDDDDD"
        
        return service_name, response


# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.test_service

test_service = CustomService(service_name)

test_service.run()