# Post-MVP Roadmap & Capability Backlog

*Status: Planning Document*
*Last Updated: $(date)*

**This document contains all planned, aspirational, and future-facing capabilities that are NOT part of the current, verified KGAS system. It serves as a backlog for future development phases.**

---

## 1. Deprecated & Pruned Capabilities (Formerly the "121-Tool Menagerie")

The following high-level capabilities and tools were part of the original design but have been pruned to focus on a core, stable MVP. They are retained here as a backlog for potential future implementation.

- **Advanced Retrieval (Phase 4):** Complex query transformation, subgraph retrieval, etc.
- **Advanced Analysis (Phase 5):** Sophisticated graph algorithms beyond PageRank.
- **Interface & UI (Phase 7):** All user interface and visualization tools.
- *...and other pruned tools from the original catalog...*

---

## 2. Future Architectural Enhancements

- **High-Availability (HA) Deployment:** Adapting the system for a production environment with database replication, failover, and load balancing.
- **LLM-Generated Theories:** Building a service that allows a Large Language Model to dynamically create new theory schemas.
- **Advanced Provenance:** Extending the provenance model to include more granular details as per the W3C PROV standard.
- **Hardened Security:** Implementing format-preserving tokenization for PII and comprehensive log redaction.

---

## 3. Future Performance & Quality Enhancements

- **Empirical Benchmarking:** Establishing a formal benchmarking suite with reference hardware to make verifiable performance claims.
- **Confidence Calibration:** Creating a canonical calibration dataset and service to ensure all confidence scores are comparable and scientifically sound.
- **Automated Vector Index Health Monitoring:** Building and deploying the `recall@k` testing service to monitor and refresh the vector index. 