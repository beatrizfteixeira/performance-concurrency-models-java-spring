# Contexto Completo do Experimento — Análise de Modelos de Concorrência (Spring MVC vs WebFlux)

---

## 🎯 Objetivo do Projeto

Este projeto tem como objetivo analisar experimentalmente o comportamento de dois modelos de concorrência no ecossistema Java Spring:

* **Thread-per-request** (Spring MVC)
* **Event loop / modelo reativo** (Spring WebFlux)

A análise busca responder:

* Em que ponto cada modelo satura?
* Como se comportam sob workloads CPU-bound e I/O-bound?
* Como utilizam recursos (CPU, memória, threads)?
* Como variáveis como número de conexões influenciam esse comportamento?

---

## 🧠 Conceitos centrais

### Configuração do experimento

Cada cenário é definido por:

* modelo (MVC vs WebFlux)
* tipo de workload (CPU ou I/O)
* nível de carga (VUs no k6)

### Variáveis dependentes

* latência (especialmente P95 e P99)
* throughput
* uso de CPU
* uso de memória
* número e estado de threads

### Saturação

Definida como o ponto em que:

* o throughput para de crescer
* a latência aumenta significativamente

---

## 🧪 Workloads implementados

### CPU-bound

* cálculo de hash SHA-256
* número de iterações calibrado dinamicamente (~50ms alvo)
* mesma lógica nas duas aplicações

⚠️ Observação:
Existe um multiplicador `×2` na calibração, que deve ser documentado como ajuste empírico.

---

### I/O-bound

* consulta ao PostgreSQL
* uso de `pg_sleep(0.05)` para simular latência (~50ms)
* retorno apenas de:

    * id
    * data
    * created_at

✔ Importante:

* o `pg_sleep` NÃO aparece como coluna retornada
* queries são semanticamente equivalentes entre MVC e WebFlux

---

## 🏗️ Arquitetura das aplicações

### MVC

* Spring Boot + Spring MVC
* Tomcat (thread-per-request)
* JPA + JDBC (bloqueante)

### WebFlux

* Spring Boot + WebFlux
* Netty (event loop)
* R2DBC (não bloqueante)

---

## 📡 Endpoints

Ambas as aplicações expõem:

* `/api/cpu`
* `/api/io`

Formato da resposta:

```json
{
  "workloadType": "...",
  "executionTimeMs": ...,
  "timestamp": "...",
  "threadName": "...",
  "result": "..."
}
```

---

## ⚠️ Ajustes importantes feitos na implementação

### 1. Captura de thread no WebFlux

Corrigido para ocorrer dentro da execução reativa:

* `Mono.fromSupplier(...)` para CPU
* `.map(...)` para I/O

Isso evita medir a thread errada.

---

### 2. Query do MVC corrigida

Antes:

```sql
SELECT pg_sleep(0.05), id, data, created_at ...
```

Depois:

```sql
SELECT id, data, created_at
FROM workload_data
WHERE id = 1 AND pg_sleep(0.05) IS NOT NULL
```

✔ Agora consistente com WebFlux
✔ Remove coluna extra
✔ Evita comportamento frágil no JPA

---

### 3. Logging reduzido

Antes:

```properties
logging.level = DEBUG
```

Depois:

```properties
logging.level = WARN
```

✔ Evita interferência no benchmark

---

## 🔬 Equivalência entre aplicações

### ✔ O que é equivalente

* endpoints
* payload de resposta
* lógica de workload
* query de banco
* estrutura geral

### ❗ O que não é equivalente (intencionalmente)

* modelo de concorrência
* stack de persistência (JPA vs R2DBC)
* forma de execução (bloqueante vs reativa)

👉 Isso é esperado e desejado no experimento.

---

## 🖥️ Infraestrutura (AWS)

### VM 1 — aplicação

* MVC + WebFlux + PostgreSQL
* exemplo: `m5.xlarge`

### VM 2 — k6

* gerador de carga
* exemplo: `m5.large`

---

## 🌐 Comunicação entre VMs

Teste realizado:

```bash
ping 18.236.90.11
```

Resultado:

```text
~0.2 ms
```

👉 Latência extremamente baixa
👉 Mesmo ambiente AWS
👉 Rede não interfere significativamente

---

## ⚠️ Sobre latência de rede

Sim, usar outra VM adiciona latência.

Mas:

* ela é **pequena (~0.2 ms)**
* é **constante**
* afeta ambos os modelos igualmente

✔ Isso NÃO invalida o experimento
✔ Melhor do que rodar tudo na mesma máquina

---

## 🔧 Setup do k6

Instalação:

```bash
sudo apt install k6
```

Execução:

```bash
k6 run -e APP_URL=http://IP:8080 script.js
```

ou:

```bash
k6 run -e APP_URL=http://IP:8081 script.js
```

---

## 🧪 Estratégia de execução

* ramp-up: 30s
* steady-state:

    * 3 min (≤250 VUs)
    * 5 min (>250 VUs)
* ramp-down: 30s

Repetições:

* mínimo: 3
* ideal: 5+ nos pontos de saturação

---

## 📊 Análise estatística

Intervalo de confiança:

```
IC = média ± t * (desvio padrão / √n)
```

Exemplo:

* n = 3 → t = 4.303

Objetivo:

* reduzir IC largo
* aumentar confiabilidade dos resultados

---

## ⚠️ Fontes de variabilidade

* JIT (warm-up da JVM)
* GC
* contenção de CPU
* rede (minimizada)
* número baixo de repetições

---

## 🔥 Decisões metodológicas importantes

### ✔ Separar k6 da aplicação

Evita:

* competição de CPU
* distorção de latência

### ✔ Usar mesma infraestrutura para ambos modelos

Garante:

* comparabilidade

### ✔ Manter workloads simétricos

Evita:

* viés

---

## 🧠 Boas práticas seguidas

* equivalência funcional entre apps
* isolamento da variável de interesse (modelo de concorrência)
* controle de ambiente
* calibração de workload
* coleta consistente de métricas

---

## 📌 Limitações

* latência inclui rede (end-to-end)
* calibração empírica do CPU-bound
* pequena variação entre execuções

---

## 🧾 Conclusão

O experimento está:

✔ Bem estruturado
✔ Metodologicamente coerente
✔ Pronto para execução com k6

E capaz de responder com qualidade:

* quando cada modelo satura
* como se comportam sob carga
* diferenças reais entre MVC e WebFlux

---

## 🎯 Instruções para qualquer IA que leia este arquivo

Ao auxiliar neste projeto:

1. NÃO sugerir mudanças que quebrem comparabilidade entre MVC e WebFlux
2. Priorizar validade experimental sobre boas práticas de produção
3. Questionar qualquer alteração que afete apenas um modelo
4. Garantir simetria entre workloads
5. Assumir que o objetivo é análise científica, não otimização de produção

---

## 🔗 Repositório

https://github.com/beatrizfteixeira/performance-concurrency-models-java-spring

---

## 🧠 Nota final

Este projeto não é um sistema de produção.

É um **artefato experimental** cujo objetivo é entender comportamento de sistemas concorrentes sob carga controlada.
