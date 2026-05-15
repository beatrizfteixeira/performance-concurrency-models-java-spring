# Apps I/O — estrutura separada

Cada framework (MVC / WebFlux) foi dividido em **dois módulos**: um para PostgreSQL e outro para API downstream HTTP.

| Módulo | Workload | Endpoint | Porta default | Main class |
|--------|----------|----------|---------------|------------|
| `app-mvc-io-http` | API downstream | `/api/io-http` | 8080 | `MvcIoHttpApplication` |
| `app-mvc-io-db` | PostgreSQL `pg_sleep` | `/api/io` | 8082 | `MvcIoDbApplication` |
| `app-webflux-io-http` | API downstream | `/api/io-http` | 8081 | `WebFluxIoHttpApplication` |
| `app-webflux-io-db` | PostgreSQL R2DBC `pg_sleep` | `/api/io` | 8083 | `WebFluxIoDbApplication` |

## Subir localmente

```bash
# MVC HTTP (cenário atual da Fase B)
cd app-mvc-io-http
mvn spring-boot:run -Dspring-boot.run.arguments="--server.port=8080 --server.tomcat.threads.max=800"

# WebFlux HTTP
cd app-webflux-io-http
mvn spring-boot:run

# MVC PostgreSQL (subir Postgres antes — ver secao abaixo)
cd app-mvc-io-db
mvn spring-boot:run

# WebFlux PostgreSQL
cd app-webflux-io-db
mvn spring-boot:run
```

## PostgreSQL em Docker (benchmark)

Para rodar `app-mvc-io-db` e `app-webflux-io-db` com `max_connections` alto e tabela `workload_data` já criada:

```bash
cd downstream-service/docker/postgres
docker compose up -d
```

Detalhes, variáveis (`HIKARI_MAX_POOL_SIZE`, `R2DBC_POOL_MAX_SIZE`, etc.) e checagens: [`downstream-service/docker/postgres/README.md`](downstream-service/docker/postgres/README.md).  
Exemplo de variáveis para copiar/colar: [`downstream-service/docker/postgres/env.example`](downstream-service/docker/postgres/env.example).

## Variáveis úteis

**HTTP (downstream):**
- `DOWNSTREAM_URL` — URL base do downstream-service (ex: `http://172.31.x.x:9090`)

**DB:**
- `SPRING_DATASOURCE_URL` / `SPRING_R2DBC_URL`
- `HIKARI_MAX_POOL_SIZE` / `R2DBC_POOL_MAX_SIZE`
- `WORKLOAD_IO_DB_SLEEP_SECONDS` — duração do `pg_sleep` (default `0.1`)

**MVC:**
- `TOMCAT_THREADS_MAX`, `TOMCAT_THREADS_MIN_SPARE`, etc.

## Apps legados

`app-mvc-io` e `app-webflux-io` mantêm código comentado dos dois cenários no mesmo projeto. **Use os módulos `-http` e `-db` acima** para experimentos novos.
