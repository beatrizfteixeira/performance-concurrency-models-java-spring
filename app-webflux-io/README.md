# app-webflux-io (legado)

Este módulo combinava HTTP downstream + PostgreSQL R2DBC no mesmo projeto (um cenário ativo, outro comentado).

**Use os módulos separados:**

- [`../app-webflux-io-http`](../app-webflux-io-http) — `/api/io-http` (porta 8081)
- [`../app-webflux-io-db`](../app-webflux-io-db) — `/api/io` com R2DBC (porta 8083)

Ver também [`../APPS-IO.md`](../APPS-IO.md).
