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
- Add user :
    forma: ```user_mail_password```
- Log user :
    forma: ```mail_password```
- Hacer reviews :
    forma: ```userid_mangaid_rating_reviewtext```
- Get reviews :
    forma: ```mangaid_userid*optional```
- Promocionar :
    forma: ```mangaid numero dias/semanas```
- Modificar :
    forma: ```mangaid|TagAmodificar|valornuevo```
- Agregar :
    forma: ```titulo|genero|formato|publicacion estatus|release date|sales|rentals|price|availableonline|copias fisicas disp|fecha de creacion*opcional|```
- Eliminar :
    forma: ```id```
- Get inventory :
    forma: ```id/all```
