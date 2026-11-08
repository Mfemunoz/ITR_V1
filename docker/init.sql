CREATE TABLE IF NOT EXISTS docker_connection_test (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO docker_connection_test (message)
VALUES ('Conexión inicial para validar la comunicación entre contenedores');
