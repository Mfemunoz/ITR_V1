
"""Prueba automatizada de comunicación entre ITR y PostgreSQL."""

import os
import sys
import uuid

import psycopg


def main() -> int:
    config = {
        "host": os.getenv("DB_HOST", "db"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "itr_db"),
        "user": os.getenv("DB_USER", "itr_user"),
        "password": os.getenv("DB_PASSWORD", "itr_password"),
        "connect_timeout": 5,
    }

    test_message = f"Jenkins Docker test: {uuid.uuid4()}"

    try:
        with psycopg.connect(**config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO docker_connection_test (message)
                    VALUES (%s)
                    RETURNING id, message
                    """,
                    (test_message,),
                )
                inserted = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT id, message
                    FROM docker_connection_test
                    WHERE id = %s
                    """,
                    (inserted[0],),
                )
                recovered = cursor.fetchone()

                if recovered != inserted:
                    raise RuntimeError(
                        "El registro recuperado no coincide con el insertado."
                    )

                cursor.execute(
                    """
                    SELECT current_database(), inet_server_addr()
                    """
                )
                database, server = cursor.fetchone()

        print("PRUEBA EXITOSA: INSERT + SELECT + COMPARACIÓN")
        print(f"Base de datos: {database}")
        print(f"Servidor PostgreSQL: {server}")
        print(f"Registro insertado y recuperado: {recovered[0]}")
        print(f"Mensaje validado: {recovered[1]}")
        return 0

    except Exception as exc:
        print(f"ERROR EN LA PRUEBA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
