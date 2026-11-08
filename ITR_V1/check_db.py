"""Verifica la comunicación desde el contenedor ITR hacia PostgreSQL."""

import os
import sys

import psycopg
from psycopg.rows import dict_row


def main() -> int:
    config = {
        "host": os.getenv("DB_HOST", "db"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "itr_db"),
        "user": os.getenv("DB_USER", "itr_user"),
        "password": os.getenv("DB_PASSWORD", "itr_password"),
        "connect_timeout": 5,
        "row_factory": dict_row,
    }

    try:
        with psycopg.connect(**config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT current_database() AS database, "
                    "inet_server_addr() AS server_address, "
                    "COUNT(*) AS test_records "
                    "FROM docker_connection_test"
                )
                result = cursor.fetchone()

        print("CONEXIÓN EXITOSA: el contenedor ITR se comunicó con PostgreSQL.")
        print(f"Base de datos: {result['database']}")
        print(f"Servidor PostgreSQL: {result['server_address']}")
        print(f"Registros de prueba: {result['test_records']}")
        return 0
    except Exception as exc:
        print(f"ERROR DE CONEXIÓN: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
