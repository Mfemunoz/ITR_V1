# ITR_V1 – Plataforma de Gestión y Planeación Logística

**Sistema de apoyo al Desarrollo Logístico – Sodimac Colombia**

## 1. Descripción del proyecto

ITR_V1 es una plataforma tecnológica orientada a la gestión, planeación, seguimiento y análisis de procesos logísticos, desarrollada para apoyar la toma de decisiones operativas y optimizar los procesos de abastecimiento y transporte.

La solución integra diferentes módulos funcionales que permiten centralizar información, facilitar el análisis de datos y proporcionar herramientas para el control de las operaciones logísticas.

El proyecto surge de la necesidad de fortalecer la gestión de los procesos de abastecimiento, transporte y distribución mediante herramientas tecnológicas, automatización y análisis de información.

## 2. Objetivo general

Desarrollar una plataforma integral de gestión logística que permita centralizar procesos operativos, facilitar la planeación del abastecimiento, optimizar la gestión del transporte y proporcionar información para el seguimiento y la toma de decisiones.

## 3. Módulos de la plataforma

La aplicación cuenta con los siguientes módulos:

| Módulo | Descripción |
|---|---|
| Centro de Control | Acceso centralizado a la plataforma y sus funcionalidades. |
| Planeación ITR | Herramientas de apoyo a la planeación logística y de abastecimiento. |
| Modelo Transporte | Generación y análisis de órdenes de despacho sugeridas, tipologías vehiculares y costos. |
| Ejecución Abastecimiento | Apoyo a la gestión de la ejecución de los procesos de abastecimiento. |
| TMS | Módulo orientado a la gestión de operaciones de transporte. |
| Consultas | Acceso a información y consultas operativas. |
| Reportes | Visualización y generación de información para seguimiento y análisis. |

## 4. Tecnologías utilizadas

El proyecto utiliza tecnologías orientadas al desarrollo de aplicaciones, procesamiento de información y administración de bases de datos.

- **Python 3.11:** lenguaje principal de desarrollo.
- **Streamlit:** construcción de la interfaz de usuario.
- **PostgreSQL 16:** gestión y almacenamiento de información.
- **Docker:** creación y ejecución de contenedores.
- **Docker Compose:** administración y orquestación de los servicios.
- **Git y GitHub:** control de versiones y administración del código fuente.

## 5. Arquitectura de la solución

La implementación utiliza una arquitectura basada en dos contenedores independientes que se comunican mediante una red interna de Docker.

### Contenedor 1: Aplicación Streamlit

Encargado de ejecutar la plataforma ITR_V1, procesar las solicitudes de los usuarios y proporcionar la interfaz de interacción.

- Imagen construida a partir de Python 3.11.
- Ejecución de Streamlit.
- Puerto de acceso: 8501.

### Contenedor 2: Base de datos PostgreSQL

Encargado de proporcionar el servicio de almacenamiento y consulta de información.

- PostgreSQL 16 Alpine.
- Puerto interno: 5432.
- Persistencia de información mediante volumen Docker.

### Comunicación entre contenedores

Los servicios se encuentran conectados mediante una red privada administrada por Docker Compose, permitiendo que la aplicación establezca conexiones con PostgreSQL sin necesidad de publicar la base de datos directamente en el equipo anfitrión.

## 6. Estructura del proyecto

```text
ITR_V1/
│
├── .devcontainer/
│
├── docker/
│
├── ITR_V1/
│   ├── requirements.txt
│   └── Archivos de la aplicación
│
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 7. Ejecución del proyecto con Docker

### Requisitos previos

- Windows, Linux o macOS.
- Git.
- Docker Desktop o Docker Engine.
- Docker Compose.
- WSL 2 para entornos Windows que utilicen el motor Linux de Docker.

### Clonar el repositorio

```bash
git clone https://github.com/Mfemunoz/ITR_V1.git
```

### Ingresar al directorio

```bash
cd ITR_V1
```

### Seleccionar la rama de la entrega

```bash
git switch entrega-semana-3-docker
```

### Construir e iniciar los contenedores

```bash
docker compose up --build -d
```

### Verificar el estado de los servicios

```bash
docker compose ps
```

### Consultar los registros de ejecución

```bash
docker compose logs
```

### Acceder a la aplicación

Una vez iniciados correctamente los servicios, ingresar desde el navegador a:

http://localhost:8501

### Detener los contenedores

```bash
docker compose down
```

Este comando detiene y elimina los contenedores y la red del proyecto, pero conserva el volumen persistente de PostgreSQL.

## 8. Validación de la comunicación

Como parte de la implementación se realizó una prueba de conectividad desde el contenedor de la aplicación hacia PostgreSQL mediante Python y la librería Psycopg.

La consulta permitió verificar:

- Establecimiento de conexión con PostgreSQL.
- Identificación de la base de datos `itr_db`.
- Obtención de la dirección IP interna del servidor.
- Ejecución satisfactoria de una consulta SQL.

Esta validación permitió comprobar la comunicación efectiva entre los dos contenedores.

## 9. Resultados de la implementación

La implementación de Docker permitió:

- Separar la aplicación y la base de datos en contenedores independientes.
- Establecer comunicación entre los servicios mediante una red interna.
- Facilitar la construcción y ejecución de los componentes mediante Docker Compose.
- Implementar persistencia de información para PostgreSQL.
- Disponer de un entorno de ejecución reproducible y organizado.
- Verificar el funcionamiento de la plataforma y sus módulos principales.

## 10. Propósito y evolución del proyecto

ITR_V1 busca evolucionar hacia una plataforma de gestión logística cada vez más integrada, incorporando herramientas de automatización, análisis de información, trazabilidad y optimización de procesos.

La implementación de Docker constituye una etapa importante en la evolución tecnológica del proyecto, al permitir organizar sus componentes y establecer una base para futuras integraciones y procesos de integración continua.

---

**Proyecto:** ITR_V1  
**Repositorio:** https://github.com/Mfemunoz/ITR_V1  
**Rama de implementación:** entrega-semana-3-docker  
**Tecnologías principales:** Python, Streamlit, PostgreSQL y Docker.

*Desarrollo orientado a la transformación digital de los procesos logísticos y al fortalecimiento de la toma de decisiones operativas.*
