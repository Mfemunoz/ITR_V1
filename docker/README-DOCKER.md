# Entrega Semana 3: Docker aplicado a ITR_V1

## Objetivo

Ejecutar la aplicación ITR_V1 y una base de datos PostgreSQL en dos contenedores independientes que se comunican por una red privada de Docker.

## Arquitectura

- **itr_app**: aplicación Streamlit basada en Python 3.11. Se publica en el puerto 8501 del computador.
- **db**: PostgreSQL 16. Utiliza el puerto interno 5432 y no se expone directamente al computador.
- **itr_network**: red Docker bridge que permite que la aplicación encuentre la base de datos mediante el nombre de servicio `db`.

La aplicación continúa leyendo y procesando archivos Excel como lo hace actualmente. El script `ITR_V1/check_db.py` demuestra la comunicación entre los contenedores con una consulta SQL real.

## Requisitos

- Docker Desktop instalado y en ejecución.
- Docker Compose v2.
- Repositorio clonado localmente.

## Construir y ejecutar

Desde la carpeta raíz del repositorio:

```bash
docker compose up --build -d
```

Revisar el estado de ambos contenedores:

```bash
docker compose ps
```

Abrir la aplicación:

```
http://localhost:8501
```

## Evidencia de comunicación

Ejecutar el cliente de prueba desde el contenedor de la aplicación:

```bash
docker compose exec itr_app python ITR_V1/check_db.py
```

La salida debe indicar que la conexión fue exitosa y mostrar el nombre de la base de datos.

También puedes consultar PostgreSQL directamente:

```bash
docker compose exec db psql -U itr_user -d itr_db -c "SELECT * FROM docker_connection_test;"
```

## Detener

```bash
docker compose down
```

Para borrar también el volumen de datos de PostgreSQL (acción destructiva):

```bash
docker compose down -v
```

## Consideraciones

- Las credenciales incluidas son únicamente para una demostración académica local. No deben reutilizarse en producción.
- La contraseña se define en `docker-compose.yml` para simplificar la práctica. En un despliegue real debe gestionarse mediante secretos o variables de entorno protegidas.
- No se migró la lógica de abastecimiento ni los archivos Excel a PostgreSQL; la base de datos se incorpora para demostrar comunicación entre contenedores.
