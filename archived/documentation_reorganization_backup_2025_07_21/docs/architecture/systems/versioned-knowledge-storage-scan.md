# Market Scan: Versioned Knowledge Storage Solutions

*Status: Initial Draft*

## 1. Overview

This document provides a comparative analysis of potential off-the-shelf solutions to replace the initial, filesystem-based `TheoryRepository` stub. The goal is to find a "buy" solution that provides robust, `git`-like versioning semantics (branch, commit, merge, diff) for structured data like our theory JSONs.

## 2. Key Requirements

- **Versioning:** Must support immutable, historical versions of data.
- **Branching & Merging:** Core requirement for evolving theories.
- **Queryability:** Must be able to query specific versions of a theory.
- **Python Integration:** Must have a mature Python client library.
- **Structured Data:** Must handle JSON/dictionary-like data natively.
- **Performance:** Should be performant for our expected scale (thousands of versions, not billions).

---

## 3. Shortlisted Candidates

### A. Git & Git LFS (Large File Storage)

- **Description:** Use a standard Git repository to store theory JSON files. Git handles the versioning, branching, and merging. Git LFS helps manage larger files efficiently.
- **Pros:**
    - **Universal:** Every developer understands Git.
    - **Mature:** The most battle-tested version control system in existence.
    - **Excellent Tooling:** Rich ecosystem of tools and hosting (GitHub, GitLab).
    - **Simple Integration:** Mature Python libraries like `GitPython` make it easy to interact with a local repo.
- **Cons:**
    - **Not a Database:** Not designed for programmatic queries over content (e.g., "find all theories with field X=Y"). It versions files, not the data inside them.
    - **Merge Conflicts:** Merging complex JSON files in Git can be notoriously difficult and often requires manual intervention.
- **Integration Sketch:** The `TheoryRepository` implementation would use `GitPython` to programmatically `git add`, `commit`, `branch`, and `checkout` files in a local repository directory.

### B. Dolt / DoltHub

- **Description:** Pitched as "Git for Data." It's a relational SQL database that you can branch, merge, and diff like a Git repository.
- **Pros:**
    - **Git Semantics:** Provides the exact `git`-like workflow we need.
    - **SQL Interface:** Data is stored in tables and can be queried with standard SQL. This is a huge advantage for querying inside versions.
    - **DoltHub:** Provides a GitHub-like experience for collaborating on databases.
- **Cons:**
    - **Relational Model:** We would need to "shred" our JSON theories into a relational schema (e.g., a `theory_versions` table, a `fields` table). This adds a layer of mapping complexity.
    - **Maturity:** Newer than Git, but very robust and well-supported.
- **Integration Sketch:** The `TheoryRepository` would connect to a local Dolt database instance using a standard Python SQL connector (like `mysql-connector-python`, as it's MySQL-compatible). Commits and branches would be issued as SQL commands.

### C. TerminusDB

- **Description:** A purpose-built, open-source knowledge graph database designed from the ground up for collaboration and revision control.
- **Pros:**
    - **Native Versioning:** Branching, merging, and time-travel are core, first-class features.
    - **Graph-Oriented:** Designed for graph data, making it a natural fit for our knowledge-centric theories. Stores data as JSON-LD.
    - **Schema-Driven:** Strong schema enforcement ensures data quality.
- **Cons:**
    - **Learning Curve:** Uses its own query language (WOQL) and data model. Requires learning a new system.
    - **Ecosystem:** Smaller community and ecosystem compared to Git or SQL-based solutions.
- **Integration Sketch:** The `TheoryRepository` would use the `terminusdb-client` for Python to connect to a TerminusDB instance. All operations would be performed via this client.

## 4. Initial Recommendation

For the **KGAS** project, **Dolt** appears to present the best trade-off between power and complexity.

- It directly provides the required **`git`-like workflow** for data versioning.
- Its use of a **standard SQL interface** avoids the need to learn a custom query language (like TerminusDB's WOQL) and leverages a massive existing ecosystem of tools and developer knowledge.
- While it requires mapping our JSON to a relational schema, this is a well-understood problem and forces us to have a more structured and queryable representation of our theories, which is a long-term benefit.

**Next Step:** When the time comes to move past the filesystem stub, the first proof-of-concept should be built using Dolt. 