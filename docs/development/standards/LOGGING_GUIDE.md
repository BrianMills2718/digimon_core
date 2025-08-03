# Logging Guide

All microservices use `structlog` ➜ stdout.  
Log schema: {ts, level, service, run_id, theory_id, msg}.  
In development `LOG_LEVEL=DEBUG`, production `INFO`.  
Use `docker logs` or `journalctl -u kgas` to read. 