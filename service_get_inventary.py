# Ejemplo de servicio
from soa_service import Soa_Service
from util.list_of_services import service

class Get_Inventary(Soa_Service):
    # ACA SE HACE LA MAGIA XD
    def process_data(self, request):
        global service_name
        
        response = "XDDDDDD" + request + "XDDDDDD"
        
        return service_name, response



# Si vas a agregar un service tienes que hacerlo en util/list_of_services.py, de esa forma todo el sistema puede saber de ese service que creaste.
# Aquí tienes que seleccionar el service que vas a usar.
service_name = service.get_inventory

test_service = Get_Inventary(service_name)

test_service.run()