# comandos dentro de la carpeta con todos los files

# Build the Docker image
sudo docker build -t custom-postgres .

# Run a new container from the custom PostgreSQL image
sudo docker run --name my_postgres_container -e POSTGRES_PASSWORD=1234 -d custom-postgres

# Para abrir el postgres docker
sudo docker exec -it my_postgres_container bash

# Conectarse
    1)psql -U postgres
    2)\c manga_db
    
# Desconectarse
    1)\q

# Para sacarle el ip al contenedor del docker (comando se hace fuera del docker, en el terminal local)
sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' my_postgres_container

