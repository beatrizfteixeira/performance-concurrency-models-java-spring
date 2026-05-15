-- Tabela usada pelos endpoints /api/io (MVC JPA + WebFlux R2DBC).
-- O init roda apenas na primeira subida do volume (volume novo).

CREATE TABLE IF NOT EXISTS workload_data (
    id         BIGINT PRIMARY KEY,
    data       VARCHAR(100),
    created_at TIMESTAMP WITHOUT TIME ZONE
);

INSERT INTO workload_data (id, data, created_at)
VALUES (1, 'benchmark-seed', NOW())
ON CONFLICT (id) DO UPDATE
SET data = EXCLUDED.data,
    created_at = EXCLUDED.created_at;
