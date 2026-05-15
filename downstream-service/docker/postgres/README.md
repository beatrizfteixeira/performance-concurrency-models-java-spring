# PostgreSQL em Docker (benchmark TCC)

Stack para testar a hipótese do orientador: **PostgreSQL com `max_connections` alto + pools JDBC/R2DBC grandes**, evitando que o pool do banco seja o único gargalo artificial.

## Subir o banco

```bash
cd performance-concurrency-models-java-spring/downstream-service/docker/postgres
cp env.example .env   # opcional: ajuste POSTGRES_SHARED_BUFFERS etc.
docker compose up -d
```

Validar:

```bash
docker exec -it postgres-benchmark-tcc psql -U testuser -d testdb -c "SHOW max_connections;"
docker exec -it postgres-benchmark-tcc psql -U testuser -d testdb -c "SELECT id, data FROM workload_data WHERE id = 1;"
```

Parar (mantém volume com dados):

```bash
docker compose down
```

Apagar volume e recriar do zero:

```bash
docker compose down -v
docker compose up -d
```

## Credenciais e porta

| Variável | Default |
|----------|---------|
| `POSTGRES_DB` | `testdb` |
| `POSTGRES_USER` | `testuser` |
| `POSTGRES_PASSWORD` | `testpass` |
| Porta host | `5432` (`POSTGRES_PORT`) |

Alinhado com `app-mvc-io-db` e `app-webflux-io-db` (`application.properties`).

## Configuração do servidor (via `docker-compose.yml` + `.env`)

| Parâmetro | Default sugerido | Nota |
|-----------|------------------|------|
| `max_connections` | `2000` | Folga acima de 1500 VUs |
| `shared_buffers` | `256MB` | Em máquina grande, suba para `4GB` (veja `env.example`) |
| `work_mem` | `1MB` | Ok para `pg_sleep`; evita pico de memória com muitas sessões |
| `synchronous_commit` | `off` | Benchmark; não use em produção |

## Apps (MVC / WebFlux DB)

Na mesma máquina que o Docker, use as URLs de `env.example` ou exporte:

```bash
export SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/testdb
export HIKARI_MAX_POOL_SIZE=1500
export HIKARI_MIN_IDLE=1500

export SPRING_R2DBC_URL=r2dbc:postgresql://localhost:5432/testdb
export R2DBC_POOL_INITIAL_SIZE=1500
export R2DBC_POOL_MAX_SIZE=1500
```

Se a app rodar **em outro host** (ex.: EC2 Apps e Postgres no mesmo host do Docker em outra VM), troque `localhost` pelo IP/hostname do servidor onde o `docker compose` está exposto.

## Limites do SO (ulimit)

O `docker-compose.yml` já define `ulimits.nofile` alto para o container.

No host Linux, se aparecer erro de “too many open files”:

```bash
ulimit -n 65535
```

Persistência: `limits.conf` / `systemd` conforme documentação do seu SO.

## Diagnóstico durante carga

```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'testdb';

SELECT state, wait_event_type, wait_event, count(*)
FROM pg_stat_activity
WHERE datname = 'testdb'
GROUP BY 1, 2, 3
ORDER BY count(*) DESC;
```

## Relação com o downstream-service HTTP

O **downstream-service** (porta 9090) continua sendo o serviço de delay HTTP para `app-*-io-http`.  
Esta pasta `docker/postgres` só sobe o **PostgreSQL** para os módulos `app-*-io-db`.
