# Ejemplo de servicio específico
from test_2 import Soa_Service

class CustomService(Soa_Service):
    def process_data(self, data):

        response = "00013serviMADRE_MIA_WILY_XD"
        
        return response


test_service = CustomService()

test_service.run()