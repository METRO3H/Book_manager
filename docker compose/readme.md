# Acceder a Postgres desde un terminal (opcional)
    
    sudo docker exec -it my_postgres_container bash 

- Conectarse a postgres
    1) ```psql -U postgres```
    2) ```\c manga_db```
    
- Desconectarse
    1) \q


# Para sacarle el ip al contenedor del docker
```sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' my_postgres_container```

# comandos utiles
1) para ver contenedores, sin -a ven solo los contenedores corriendo: 
```sudo docker ps -a```
2) para borrar una imagen: ```sudo docker rmi nombreimage```
3) para entrar a un contenedor en modo terminal: ```sudo docker exec -it containernombre/ID bash```
4) para salir del modo terminal de un docker: ```ctrl+d```
5) si tienen problemas para hacer cambios en los archivos de creacion de la db y el docker file recomiendo hacer: ```sudo docker compose down```
6) destruccion total docker cosas que no se ocupan: ```docker system prune -f```
7) para correr detener/empezar el contentedor: ```sudo docker stop/start containerName```
