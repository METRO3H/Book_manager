<<<<<<< HEAD
# SI TIENE VERSION ANTIGUA

    sudo docker stop my_postgres_container
    sudo docker rmi -f ID_DE_LA_IMAGEN_PSQL_OLD
=======

# Iniciar servidor con carpeta web dielo 
revisar dependencias en el py antes para evitar problemas
    
    
    sudo python3 app.py
>>>>>>> 2bd06ab6ce5f90bbd23ccd859820bbb7aa5c70c4
    
# Ejecutar la base de datos Postgres con Docker y EL BUS SOA
(dentro de carpeta docker compose)

**Construir la imagen de Docker**

  
    sudo docker compose up -d


# Usar cliente
Usar cliente.py para comunicarse con los servicios
# Servicios
Hay que activarlos con sus .py respectivos
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
- Add wish list :
    forma: ```id_usuario/id_manga```
- Remove wish list :
    forma: ```id_usuario/id_manga```
- Get wish list :
    forma: ```id_usuario```
- Get estadisticas:
    forma: ```<nro anio>-<nro mes>-<nro dia>_anio/mes/dia```