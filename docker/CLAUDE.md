# Docker Deployment - CLAUDE.md

## Overview
The `docker/` directory contains **Docker Compose files** and production-grade container configurations for deploying the GraphRAG stack. It complements the configs under `config/environments/`.

## Directory Structure
```
docker/
└── production/
    ├── Dockerfile.app          # Optimized application image
    ├── Dockerfile.neo4j        # Slim Neo4j image with plugins
    ├── docker-compose.yml      # Production-ready stack (app + db + monitoring)
    └── entrypoint.sh           # Entrypoint for migration & health checks
```

## Build & Run
```bash
# Build application image
cd docker/production
docker build -f Dockerfile.app -t graphrag-app:latest ..

# Bring up full stack
docker compose -f docker/production/docker-compose.yml up -d
```

## Services
| Service | Port | Purpose |
|---------|------|---------|
| `app` | 8501 | Streamlit UI & API endpoints |
| `neo4j` | 7687/7474 | Graph database |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3000 | Dashboard visualization |

## Environment Variables
Set via `.env` or secrets manager:
- `OPENAI_API_KEY`
- `NEO4J_USER`, `NEO4J_PASS`
- `GRAFANA_ADMIN_PASS`

## Deployment Workflow
1. **Build Images** – `docker compose build`
2. **Push to Registry** – `docker tag && docker push`
3. **Deploy** – `docker compose pull && docker compose up -d`
4. **Verify** – `docker compose ps && docker logs <service>`

## Zero-Downtime Upgrade
```bash
docker compose pull app && docker compose up -d --no-deps app && docker image prune -f
```

## Backup & Restore
```bash
# Backup Neo4j volume
docker run --rm --volumes-from neo4j -v $(pwd):/backup busybox tar czf neo4j_backup.tar.gz /data

# Restore
docker run --rm --volumes-from neo4j -v $(pwd):/backup busybox tar xzf neo4j_backup.tar.gz -C /
```

## Troubleshooting
| Symptom | Resolution |
|---------|------------|
| Container restarts | `docker logs <service>` for stack trace |
| Neo4j not reachable | Expose ports 7474/7687, check bolt URL |
| No metrics in Grafana | Check Prometheus target discovery |
| OOM kills | Increase `mem_limit` in compose or tune Java heap |

## Security Hardening
- Run containers as non-root (`USER app` in Dockerfile).
- Use Docker secrets for passwords.
- Enable TLS termination (Traefik/Nginx) in front of the stack.
- Scan images (`trivy image graphrag-app:latest`).

## CI/CD Integration
- Images built/pushed via GitHub Actions.
- Compose deployment triggered by ArgoCD/Kubernetes in prod.
- Tags follow `git describe --tags` for traceability. 