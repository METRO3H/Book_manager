# SI TIENE VERSION ANTIGUA

    sudo docker stop my_postgres_container
    sudo docker rmi -f ID_DE_LA_IMAGEN_PSQL_OLD
    
# Ejecutar la base de datos Postgres con Docker y EL BUS SOA
(dentro de carpeta docker compose)

**Construir la imagen de Docker**

  
    sudo docker compose up -d


# Usar cliente
Usar cliente.py para comunicarse con los servicios
# Servicios
- Registro :
    Mandar por el cliente informacion de la forma: ```user_mail_password```
- Loging :
    Mandar por el cliente informacion de la forma: ```mail_password```
