---
status: living
doc-type: vision
governance: doc-governance
---

# Vision Alignment: Theory-Aware KGAS Platform

This document aligns the Knowledge Graph Analysis System (KGAS) with the dissertation 'Theoretical Foundations for LLM-Generated Ontologies and Analysis of Fringe Discourse.'

## Navigation
- [KGAS Evergreen Documentation](KGAS_EVERGREEN_DOCUMENTATION.md)
- [Roadmap](ROADMAP_v2.1.md)
- [Architecture](ARCHITECTURE.md)
- [Compatibility Matrix](COMPATIBILITY_MATRIX.md)

## Chosen Direction: Option C - Theory-Aware GraphRAG Platform

After comprehensive analysis of the original 121-tool universal platform vision, KGAS has been realigned toward a **Theory-Aware GraphRAG Platform** that prioritizes theoretical rigor and practical utility over universal format support. This decision reflects the reality that building a truly universal platform would require resources beyond current capacity while the theoretical foundation provides unique value that can be delivered incrementally.

## Implementation Strategy

The platform focuses on **GraphRAG as the primary analytical method** with theory schemas providing the conceptual framework for all processing. Rather than attempting to support every possible data format and analytical method, the system excels at extracting knowledge graphs from documents and applying social science theories to the analysis. This specialization allows for deeper theoretical integration and more meaningful insights than a broader but shallower universal platform.

## Current Status and Roadmap

Development is currently in **Phase A: Theory-Aware Architecture Foundation** with focus on establishing the service compatibility layer, phase interface contracts, and UI adapter patterns. The roadmap prioritizes getting the theoretical foundation properly integrated into the processing pipeline before expanding to additional capabilities. For detailed development status and next steps, see [`docs/planning/roadmap.md`](ROADMAP_v2.1.md).

<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
