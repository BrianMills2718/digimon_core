# Utility Scripts - CLAUDE.md

## Overview
The `scripts/` directory contains **utility scripts** for database maintenance, configuration migration, verification, and documentation preview. These scripts automate common operational tasks during development and production maintenance.

## Directory Contents
| Script | Description |
|--------|-------------|
| `backup_databases.sh` | Create timestamped Neo4j backups (with optional encryption) |
| `restore_databases.sh` | Restore backups to local or remote Neo4j instance |
| `migrate_config_references.py` | Update legacy config paths to new structure |
| `simple_verification.py` | Quick health check of core services & metrics |
| `verify_tool_success_rate.py` | Compute success-rate statistics for phase tools |
| `doc_preview.sh` | Build & open Markdown docs locally (Pandoc/Grip) |

## Usage
### Database Backup
```bash
# Full backup (development)
./scripts/backup_databases.sh --env dev --encrypt

# Backup to custom path
./scripts/backup_databases.sh --output /backups/nightly
```
### Database Restore
```bash
# Restore latest backup
./scripts/restore_databases.sh --backup /backups/nightly/latest.dump

# Restore to remote Neo4j
./scripts/restore_databases.sh --host neo4j.prod --port 7687 --backup latest.dump
```
### Config Migration
```bash
# Dry-run migration
python scripts/migrate_config_references.py --dry-run

# Apply migration
python scripts/migrate_config_references.py --apply
```
### Verification Scripts
```bash
# Quick verification (10-second smoke test)
python scripts/simple_verification.py

# Tool success-rate report (writes to logs/tool_success_rate.json)
python scripts/verify_tool_success_rate.py --days 7
```
### Documentation Preview
```bash
# Serve Markdown docs live on http://localhost:8000
./scripts/doc_preview.sh
```

## Common CLI Flags
| Flag | Scripts | Purpose |
|------|---------|---------|
| `--env` | backup/restore | Target environment (`dev`, `prod`) |
| `--encrypt` | backup | Encrypt backup with `gpg` |
| `--output` | backup | Custom output directory |
| `--host`, `--port` | restore | Target Neo4j instance |
| `--dry-run` | migrate_config_references.py | Preview changes |
| `--apply` | migrate_config_references.py | Apply changes |
| `--days` | verify_tool_success_rate.py | Time window for metrics |

## Best Practices
1. **Run Scripts in Virtualenv** – Activate venv to ensure dependencies.
2. **Use `--dry-run` First** – Especially for migration scripts.
3. **Automate via Cron** – Schedule backups & verification scripts.
4. **Store Secrets Securely** – Pass DB creds via env vars (`NEO4J_USER`, `NEO4J_PASS`).
5. **Log Outputs** – Redirect script logs to `logs/` for audit.

## Troubleshooting
| Issue | Fix |
|-------|-----|
| `gpg: command not found` | `sudo apt install gnupg` |
| `bolt connection refused` | Check Neo4j container running & `NEO4J_URL` |
| Migration script fails | Run with `--dry-run` and inspect YAML diff |

## Extending Scripts
1. Place new script in `scripts/` and make executable (`chmod +x`).
2. Follow naming convention (`<verb>_<object>.sh` or `.py`).
3. Add help output (`-h`/`--help`).
4. Update this CLAUDE.md table with description and flags. 