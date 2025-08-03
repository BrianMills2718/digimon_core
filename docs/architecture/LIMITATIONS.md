---
status: living
---

# KGAS System Limitations

**Document Version**: 2.0  
**Updated**: 2024-07-19
**Purpose**: To provide a transparent and realistic assessment of the system's architectural and operational boundaries.

## 🎯 Core Architectural Limitations

This section details fundamental design choices that define the system's operational envelope. These are not bugs, but deliberate trade-offs made to prioritize research flexibility over production-grade resilience and feature scope.

### **1. No High-Availability (HA) by Design**
- **Limitation**: The system is designed as a single-node, single-leader application. There are no built-in mechanisms for automated failover, database replication, or load balancing.
- **Consequence**: If a critical component like the Neo4j database becomes unavailable, the entire system will halt and require manual intervention to restart.
- **Rationale**: This is an academic research project. The complexity and operational overhead of implementing an HA architecture are out of scope and provide minimal value for local, single-user research workflows. The system is **not** suitable for production or business-critical deployments where uptime is a concern.

### **2. Static Theory Model (No On-the-Fly Evolution)**
- **Limitation**: The system currently treats "theories" as static, versioned JSON artifacts. To change a theory, a user must manually create a new version of the file and re-run the analysis. There is no built-in functionality for branching, merging, or otherwise managing the lifecycle of a theory within the application.
- **Consequence**: Exploring variations of a theoretical model is a manual, iterative process that happens outside the core application logic.
- **Rationale**: Building an in-app, `git`-like version control system for ontologies is a significant research project in its own right. The current design defers this complexity by using a `TheoryRepository` abstraction, which allows a more sophisticated versioning system to be plugged in later without a major refactor. (See `docs/planning/ROADMAP.md`).

### **3. Simplified PII Handling**
- **Limitation**: The system's approach to Personally Identifiable Information (PII) is designed for revocability in a research context, not for compliance with stringent regulations like GDPR or HIPAA in a production environment.
- **Consequence**: While the system includes a PII vault for recoverable encryption, it lacks the broader governance features (e.g., automated key rotation, detailed audit logs, threshold secret sharing) required for handling sensitive production data.
- **Rationale**: Implementing a full-scale, compliant PII governance system is beyond the current scope. The focus is on enabling research workflows that may require temporary access to sensitive data, with the understanding that the system is not a hardened production vault.

## 🔧 Other Technical & Operational Limitations

### Processing & Performance
- **Single-Machine Focus**: The default deployment is for a single machine; scaling is vertical (more RAM/CPU) not horizontal (distributed).
- **Memory Intensive**: Graph construction and analysis algorithms can be memory-intensive. A minimum of 8GB RAM is recommended, with 16GB+ for larger graphs.
- **API Dependencies**: System performance and cost are directly tied to the rate limits, latency, and pricing of external LLM APIs.

### Accuracy & Reproducibility
- **Domain Sensitivity**: Extraction accuracy is highest when a relevant theory schema is provided. Performance on out-of-domain documents without a guiding theory may be lower.
- **Stochastic Outputs**: While tests are seeded for determinism, some LLM-based components may exhibit stochastic (non-deterministic) behavior, leading to minor variations in output between identical runs.

---

<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for the master plan and future feature concepts.</sup>
