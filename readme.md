# BUS SOA
- El bus a usar en el proyecto está en una imagen Docker. Para ejecutarlo, tienen que ingresar el siguiente comando:

```docker
sudo docker run -d -p 5000:5000 jrgiadach/soabus:v1
```

y luego, enviar transacciones al puerto **5000** del localhost.
# Base de datos Postgres

## Pasos para configurar y ejecutar la base de datos Postgres con Docker

1. **Construir la imagen de Docker**
    ```sh
    sudo docker build -t custom-postgres .
    ```

2. **Crear y ejecutar un contenedor de Postgres**
    ```sh
    sudo docker run --name my_postgres_container -e POSTGRES_PASSWORD=1234 -d custom-postgres
    ```

3. **Acceder a Postgres desde un terminal (opcional)**
    ```sh
    sudo docker exec -it my_postgres_container bash
    ```
4. **Obtener IP de contenedor**
   ```sh
   sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' my_postgres_container
   ```

5. **Iniciar el docker de postgres si es que nada funciona**
    ```docker
    sudo docker start 89af24ee582f
    ```
# Servicios
- Registro :
    Mandar por el cliente informacion de la forma: ```user_mail_password```
- Loging :
    Mandar por el cliente informacion de la forma: ```mail_password```
