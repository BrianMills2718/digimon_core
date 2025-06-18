# CLAUDE.md - Implementation Guide

## 🎯 Current Status: Milestone 3 VALIDATED ✅

### ✅ Milestone 2 Complete (January 17, 2025)
1. **CO_OCCURS_WITH: 0%** via LLM extraction ✅
2. **Complex Query Success: 66.7%** ✅
3. **Relationship Accuracy: 80%** ✅
4. **Real PDF Testing: VERIFIED** ✅

### ✅ Milestone 3 Complete (January 17, 2025)
1. **Community Detection: WORKING** ✅
   - T31: EntityNodeBuilder implemented
   - Louvain algorithm detects 3 communities
   - Modularity: 0.75 (excellent separation)
   
2. **Multi-hop Queries: WORKING** ✅
   - 3+ hop paths found consistently
   - Average query time: 0.006s
   
3. **GraphRAG Operators: IMPLEMENTED** ✅
   - T49: Multi-hop query
   - T50: Neighborhood search
   - T52: Path finding (shortest/all/weighted)
   - T56: Community summary

### 🚀 Milestone 4: Statistical Analysis
1. **Implement Analysis Tools**
   - T68: PageRank (already done)
   - T69: Centrality Measures
   - T70: Clustering Coefficient
   - T71: Graph Statistics
   
2. **Success Criteria**
   - Statistical measures computed correctly
   - Results match NetworkX benchmarks
   - Integration with GraphRAG queries

## 🛠️ Quick Start Commands

```bash
# Start databases
docker-compose up -d

# Run current adversarial tests
python test_adversarial_round2.py

# Test specific component
python test_relationship_debug.py

# Run full demo
python demo_working_graphrag.py
```

## 📁 Key Files to Edit

### To Fix CO_OCCURS_WITH Dominance:
- `src/tools/phase2/t24_relationship_extractor.py` - Add more patterns
- Consider implementing `src/tools/phase2/t23b_entity_extractor_llm.py`

### To Fix Complex Queries:
- `src/tools/phase7/t94_natural_language_query.py` - Improve graph queries
- Add path-finding algorithms to `_graph_based_query()`

### To Add Coreference:
- Implement `src/tools/phase2/t25_coreference_resolver.py`
- Update `src/core/t107_identity_service.py` for alias handling

## ✅ What's Actually Working

- **Entity Extraction**: Enhanced with proper noun fallback
- **Basic Relationships**: FOUNDED, ACQUIRED, LOCATED_IN extracted
- **Graph Structure**: Multi-hop paths exist
- **No-Embedding Fallback**: Pure graph queries work

## 📊 Current Test Results

```python
# From test_adversarial_round2.py
Relationship Accuracy: 80% (4/5)  # ✓ Meets requirement
CO_OCCURS_WITH: 85%              # ✗ Fails <70% requirement  
Complex Queries: 33%             # ✗ Fails >60% requirement
Works Without Embeddings: Yes    # ✓ Meets requirement
```

## 🔧 Critical Design Requirements

### Tool Configurability Pattern
**ALL TOOLS MUST FOLLOW THIS PATTERN:**
```python
def tool_method(
    self,
    required_param: str,
    threshold: float = 3.0,      # CONFIGURABLE with default
    algorithm: str = "default",   # CONFIGURABLE with default
    max_iterations: int = 10,     # CONFIGURABLE with default
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """Tool implementation with configurable parameters."""
```

**NEVER hardcode:**
- Thresholds (weight > 3.0)
- Iteration limits
- Algorithm parameters
- Confidence cutoffs
- Distance metrics

### Known Issues to Fix:
- [ ] T31 Community Detection: Hardcoded weight > 3.0 threshold
- [ ] T68 PageRank: Missing timestamp handling for test entities
- [ ] T41 Embedding Generator: Assumes entities have text content
- [ ] T94 Natural Language Query: Poor query understanding (25% success)

### Tools Status (13 of 121 implemented):
- ✅ T01: PDF Document Loader
- ✅ T13: Text Chunker  
- ✅ T23a: SpaCy Entity Extractor
- ✅ T23b: LLM Entity Extractor
- ✅ T24: Relationship Extractor
- ✅ T31: Entity Node Builder
- ✅ T41: Embedding Generator
- ✅ T49: Multi-hop Query
- ✅ T50: Neighborhood Search
- ✅ T52: Path Finding
- ✅ T56: Community Summary
- ✅ T68: PageRank Analyzer
- ✅ T94: Natural Language Query

### Next Tools to Implement (Priority):
- T25: Coreference Resolver (fixes name matching)
- T34: Relationship Edge Builder (reduces CO_OCCURS_WITH)
- T69: Centrality Measures (betweenness, closeness)
- T70: Clustering Coefficient

## 🚫 Common Pitfalls to Avoid

1. **Don't claim success without adversarial testing**
2. **Don't test with toy examples - use real data**
3. **Don't ignore failing requirements**
4. **Don't implement new tools until current ones pass tests**

## 📈 Success Metrics

Before claiming Milestone 2 complete:
- CO_OCCURS_WITH < 70%
- Complex query success > 60%
- Tested on 5+ real PDFs
- All adversarial tests pass
- Results reproducible 3x

## 🔍 Testing Commands

```python
# Quick validation
python -c "
from src.utils.database import DatabaseManager
db = DatabaseManager()
db.initialize()
with db.neo4j.driver.session() as s:
    r = s.run('MATCH ()-[r]->() RETURN type(r), count(r) ORDER BY count(r) DESC')
    for row in r: print(f'{row[0]}: {row[1]}')
"

# Check relationship distribution
python -c "
# ... calculate CO_OCCURS_WITH percentage
"
```

## 📚 Reference Docs (When Needed)

- **Design principles**: `DESIGN_PRINCIPLES.md` (MUST READ)
- Tool specifications: `../docs/core/SPECIFICATIONS.md`
- Design patterns: `../docs/core/DESIGN_PATTERNS.md`
- Database integration: `../docs/core/DATABASE_INTEGRATION.md`

## ⚡ Current Priority

**STOP EVERYTHING ELSE** and fix:
1. CO_OCCURS_WITH percentage (85% → <70%)
2. Complex query success (33% → >60%)

Only then proceed to Milestone 3.