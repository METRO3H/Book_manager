El bus a usar en el proyecto está en una imagen Docker. Para ejecutarlo, tienen que ingresar el siguiente comando:

```docker
docker run -d -p 5000:5000 jrgiadach/soabus:v1
```

y luego, enviar transacciones al puerto **5000** del localhost.

La estructura de la transacción es la siguiente:

    NNNNNSSSSSDATOS

en que:

***NNNNN*** es la cantidad de caracteres que vienen a continuación.

***SSSSS*** es el nombre del servicio que se requiere usar.

***DATOS*** son los datos de la transacción.

Tanto ***NNNNN***, como ***SSSSS*** deben ser exactamente de largo 5, y DATOS del largo de los datos que se envían al servicio.

Ejemplo :

    00012sumar120 345

La transacción de respuesta tiene la misma estructura, con un agregado entre el nombre del servicio y la respuesta del servicio, que indica el resultado del proceso (OK o NK)

Ejemplo :

    00022sumarOK120 + 345 = 465