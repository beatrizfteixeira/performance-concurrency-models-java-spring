# app-mvc-io (legado)

Este módulo combinava HTTP downstream + PostgreSQL no mesmo projeto (um cenário ativo, outro comentado).

**Use os módulos separados:**

- [`../app-mvc-io-http`](../app-mvc-io-http) — `/api/io-http` (porta 8080)
- [`../app-mvc-io-db`](../app-mvc-io-db) — `/api/io` com JPA/Hikari (porta 8082)

Ver também [`../APPS-IO.md`](../APPS-IO.md).
