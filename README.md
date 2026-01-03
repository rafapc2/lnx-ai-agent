# lnx-ai-agent
demo for Leanix mcp connection


# LeanIX Agent (Docker Compose, Python)

Arquitectura local (Docker Compose) para:
- **leanix-mcp**: conector MCP/REST hacia LeanIX (structured retrieval)
- **snapshot-service**: construye snapshots versionados + score de calidad de datos
- **agent-api**: agente/orquestador simple que responde con recomendaciones **con evidencia**
- **Postgres + pgvector**: persistencia de snapshots y (opcional) embeddings
- **Redis**: cache (entity resolution / respuestas)

> Nota: este repo es un **starter kit**. Las llamadas reales a LeanIX se dejan listas para configurar por `LEANIX_*`.

---

## 1) Requisitos

- Docker + Docker Compose plugin

---

## 2) Inicio rápido

```bash
cd leanix-agent-compose
cp .env.example .env
docker compose up --build
```

Servicios:
- Agent API: http://localhost:8000/docs
- Snapshot Service: http://localhost:8001/docs
- LeanIX MCP: http://localhost:8002/docs
- Postgres: localhost:5432
- Redis: localhost:6379

---

## 3) Probar (sin LeanIX real)

1) Construir snapshot (usa datos mock si no configuras LeanIX):
```bash
curl -X POST "http://localhost:8001/snapshots/build" \
  -H "Content-Type: application/json" \
  -d '{"initiative_id":"INIT-123"}'
```

2) Pedir recomendaciones:
```bash
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"initiative_id":"INIT-123","question":"Recomiéndame acciones para reducir riesgo y modernizar"}'
```

---

## 4) Conectar a LeanIX (vía MCP)

Edita `.env` y setea:
- `LEANIX_API_BASE`
- `LEANIX_API_TOKEN` (o credenciales si tu implementación lo requiere)

El conector **leanix-mcp** expone endpoints REST tipo tools:
- `POST /fact_sheets/search`
- `GET /fact_sheets/{id}`
- `GET /relations/{id}`
- `POST /initiatives/resolve`

Integra tu MCP real ahí (o reemplaza la implementación por tu adapter MCP).

---

## 5) Estructura del proyecto

```
.
├─ docker-compose.yml
├─ .env.example
├─ db/init/001_init.sql
└─ services
   ├─ agent-api
   ├─ snapshot-service
   └─ leanix-mcp
```

---

## 6) Principios de exactitud (resumen)

- **Facts** (owners, lifecycle, relaciones) vienen del conector structured (`leanix-mcp`) + snapshot versionado.
- El agente **no inventa**: si faltan campos críticos, retorna **GAPS**.
- Toda recomendación incluye **evidence** (ids + campos + lastUpdated cuando existan).
