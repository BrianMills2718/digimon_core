# Theory Registry Implementation

**Status**: Implementation Specification  
**Purpose**: Define how theory schemas are managed, validated, and integrated in KGAS  
**Related**: [Theory Repository Abstraction](theory-repository-abstraction.md), [MCL Theory Examples](../data/mcl-theory-schemas-examples.md)

## Overview

The Theory Registry is the central component managing the lifecycle of theory schemas in KGAS. It handles theory validation, concept mapping to the Master Concept Library (MCL), and integration with the analysis pipeline.

## Architecture Components

### Core Registry Service

```python
class TheoryRegistryService:
    """Central service for theory schema management"""
    
    def __init__(self):
        self.mcl = MasterConceptLibrary()
        self.schema_validator = TheorySchemaValidator()
        self.concept_mapper = ConceptMapper()
        self.dolce_aligner = DOLCEAligner()
        self.neo4j_manager = Neo4jManager()
        
    async def register_theory(self, theory_yaml: str) -> TheoryRegistrationResult:
        """Register new theory schema with full validation pipeline"""
        
        # 1. Parse and validate YAML structure
        theory_schema = await self._parse_theory_schema(theory_yaml)
        
        # 2. Validate against schema requirements
        schema_validation = await self.schema_validator.validate(theory_schema)
        if not schema_validation.is_valid:
            return TheoryRegistrationResult(
                status="validation_failed",
                errors=schema_validation.errors
            )
        
        # 3. Map concepts to MCL canonical forms
        concept_mappings = await self._map_theory_concepts(theory_schema)
        
        # 4. Store in Neo4j with provenance
        storage_result = await self._store_theory_schema(theory_schema, concept_mappings)
        
        # 5. Register theory tools (T05 variants)
        await self._register_theory_tools(theory_schema)
        
        return TheoryRegistrationResult(
            status="registered",
            theory_id=theory_schema.id,
            concept_mappings=concept_mappings,
            tools_registered=len(theory_schema.object_types)
        )
```

### Theory Schema Validation

```python
class TheorySchemaValidator:
    """Validates theory schemas against KGAS requirements"""
    
    validation_rules = [
        "required_fields_present",      # theory_name, core_proposition, seminal_works
        "citation_format_valid",        # APA format validation
        "concept_definitions_complete", # All concepts have descriptions
        "source_ids_traceable",        # All source_ids link to seminal_works
        "mcl_mapping_valid",           # Concepts map to valid MCL entries
        "dolce_alignment_consistent",  # Upper ontology alignment
        "measurement_specs_complete"   # Properties have valid measurement specifications
    ]
    
    async def validate(self, theory: TheorySchema) -> ValidationResult:
        validation_results = []
        
        for rule in self.validation_rules:
            rule_result = await getattr(self, f"_validate_{rule}")(theory)
            validation_results.append(rule_result)
        
        return ValidationResult.aggregate(validation_results)
    
    async def _validate_mcl_mapping_valid(self, theory: TheorySchema) -> RuleValidationResult:
        """Ensure all theory concepts can be mapped to MCL canonical concepts"""
        unmapped_concepts = []
        
        for object_type in theory.object_types:
            mcl_mapping = await self.mcl.find_mapping(object_type.name, object_type.description)
            if not mcl_mapping:
                unmapped_concepts.append(object_type.name)
        
        return RuleValidationResult(
            rule="mcl_mapping_valid",
            passed=len(unmapped_concepts) == 0,
            issues=unmapped_concepts,
            recommendation="Create MCL concepts for unmapped theory concepts"
        )
```

## Theory Integration with Analysis Pipeline

### Theory-Guided Analysis Workflow

```python
class TheoryGuidedAnalysisOrchestrator:
    """Orchestrates analysis using specific theory schemas"""
    
    def __init__(self):
        self.theory_registry = TheoryRegistryService()
        self.pipeline_orchestrator = PipelineOrchestrator()
        
    async def analyze_with_theory(self, 
                                 documents: List[Document], 
                                 theory_name: str,
                                 analysis_mode: AnalysisMode = AnalysisMode.CROSS_MODAL
                                ) -> TheoryGuidedResult:
        """Execute theory-guided analysis across documents"""
        
        # 1. Retrieve theory schema and MCL mappings
        theory_schema = await self.theory_registry.get_theory(theory_name)
        mcl_concepts = await self.theory_registry.get_mcl_mappings(theory_name)
        
        # 2. Configure analysis pipeline with theory context
        pipeline_config = await self._create_theory_pipeline_config(
            theory_schema, mcl_concepts, analysis_mode
        )
        
        # 3. Execute analysis with theory-guided extraction
        results = []
        for document in documents:
            doc_result = await self._analyze_document_with_theory(
                document, theory_schema, pipeline_config
            )
            results.append(doc_result)
        
        # 4. Synthesize results using theory framework
        synthesis = await self._synthesize_theory_results(results, theory_schema)
        
        return TheoryGuidedResult(
            theory_used=theory_name,
            individual_results=results,
            synthesis=synthesis,
            confidence_assessment=self._assess_theory_fit(synthesis, theory_schema)
        )
    
    async def _analyze_document_with_theory(self, 
                                          document: Document,
                                          theory: TheorySchema,
                                          config: PipelineConfig
                                         ) -> DocumentTheoryResult:
        """Apply theory-specific analysis to single document"""
        
        # T05: Theory-guided entity extraction
        entities = await self.pipeline_orchestrator.execute_tool(
            "T05", 
            document, 
            theory_context=theory.object_types,
            mcl_concepts=config.mcl_mappings
        )
        
        # T06: Theory-guided relationship extraction  
        relationships = await self.pipeline_orchestrator.execute_tool(
            "T06",
            document,
            entities=entities,
            theory_relationships=theory.fact_types
        )
        
        # Cross-modal analysis with theory constraints
        if config.analysis_mode == AnalysisMode.CROSS_MODAL:
            graph_analysis = await self._theory_constrained_graph_analysis(
                entities, relationships, theory
            )
            table_analysis = await self._theory_constrained_table_analysis(
                entities, relationships, theory
            )
            vector_analysis = await self._theory_constrained_vector_analysis(
                document, entities, theory
            )
            
            cross_modal_result = await self._integrate_cross_modal_with_theory(
                graph_analysis, table_analysis, vector_analysis, theory
            )
            
            return DocumentTheoryResult(
                entities=entities,
                relationships=relationships,
                cross_modal_analysis=cross_modal_result,
                theory_fit_score=self._calculate_theory_fit(cross_modal_result, theory)
            )
```

## Database Integration

### Neo4j Theory Schema Storage

```cypher
// Theory schema nodes
(:Theory {
    name: "Cognitive Dissonance Theory",
    core_proposition: "Individuals are motivated to reduce...",
    registration_date: datetime(),
    validation_status: "production_ready",
    usage_count: 247,
    seminal_works: ["Festinger, L. (1957)..."]
})

// Theory concepts with MCL mappings
(:TheoryConcept {
    theory_name: "Cognitive Dissonance Theory",
    concept_name: "Individual", 
    concept_type: "EntityConcept",
    mcl_canonical_name: "SocialAgent",
    dolce_parent: "dolce:SocialAgent"
})

// Theory validation evidence
(:ValidationEvidence {
    theory_name: "Cognitive Dissonance Theory",
    validation_type: "academic_citation_analysis",
    confidence_score: 0.94,
    evidence_source: "semantic_scholar_api",
    validation_date: datetime()
})

// Relationships
(:Theory)-[:HAS_CONCEPT]->(:TheoryConcept)
(:TheoryConcept)-[:MAPS_TO]->(:MCLConcept)
(:Theory)-[:VALIDATED_BY]->(:ValidationEvidence)
```

### Theory Usage Analytics

```python
class TheoryUsageAnalytics:
    """Track and analyze theory usage patterns"""
    
    async def track_theory_usage(self, theory_name: str, analysis_context: dict):
        """Record theory usage for analytics"""
        usage_record = {
            "theory_name": theory_name,
            "timestamp": datetime.now(),
            "document_count": analysis_context.get("document_count"),
            "analysis_mode": analysis_context.get("analysis_mode"),
            "user_id": analysis_context.get("user_id"),
            "success": analysis_context.get("analysis_success", False)
        }
        
        await self.neo4j_manager.execute_cypher("""
            CREATE (:TheoryUsage $usage_record)
        """, usage_record=usage_record)
    
    async def get_theory_effectiveness_metrics(self, theory_name: str) -> TheoryMetrics:
        """Calculate theory effectiveness and usage patterns"""
        metrics = await self.neo4j_manager.execute_cypher("""
            MATCH (t:Theory {name: $theory_name})
            OPTIONAL MATCH (t)-[:USED_IN]->(usage:TheoryUsage)
            OPTIONAL MATCH (usage)-[:PRODUCED_RESULT]->(result:AnalysisResult)
            RETURN 
                t.name as theory_name,
                count(usage) as total_uses,
                avg(result.confidence_score) as avg_confidence,
                avg(result.theory_fit_score) as avg_theory_fit,
                count(CASE WHEN usage.success THEN 1 END) as successful_analyses
        """, theory_name=theory_name)
        
        return TheoryMetrics.from_neo4j_result(metrics[0])
```

## Tool Integration

### Theory-Specific Tool Generation

```python
class TheoryToolGenerator:
    """Automatically generates theory-specific analysis tools"""
    
    async def generate_theory_tools(self, theory: TheorySchema) -> List[Tool]:
        """Generate T05-variant tools for specific theory"""
        
        tools = []
        
        # T05.{theory}: Entity extraction tool
        entity_tool = await self._generate_entity_extraction_tool(theory)
        tools.append(entity_tool)
        
        # T06.{theory}: Relationship extraction tool  
        relationship_tool = await self._generate_relationship_extraction_tool(theory)
        tools.append(relationship_tool)
        
        # T20.{theory}: Theory validation tool
        validation_tool = await self._generate_theory_validation_tool(theory)
        tools.append(validation_tool)
        
        return tools
    
    async def _generate_entity_extraction_tool(self, theory: TheorySchema) -> Tool:
        """Generate theory-specific entity extraction tool"""
        
        tool_code = f"""
class T05_{theory.name.replace(' ', '_')}_EntityExtraction(Tool):
    '''Entity extraction tool for {theory.name}'''
    
    def __init__(self):
        super().__init__(
            tool_id='T05.{theory.name}',
            name='{theory.name} Entity Extraction',
            description='Extract entities using {theory.name} theoretical framework'
        )
        self.theory_concepts = {[obj.name for obj in theory.object_types]}
        self.mcl_mappings = {{{obj.name: obj.mcl_mapping for obj in theory.object_types}}}
    
    async def execute(self, document: Document) -> EntityExtractionResult:
        # Theory-guided extraction logic
        extracted_entities = await self._extract_with_theory_guidance(
            document, self.theory_concepts, self.mcl_mappings
        )
        
        # Validate against theory expectations
        validation_result = await self._validate_theory_consistency(
            extracted_entities, theory_schema={theory.to_dict()}
        )
        
        return EntityExtractionResult(
            entities=extracted_entities,
            theory_validation=validation_result,
            confidence=self._calculate_theory_confidence(validation_result)
        )
"""
        
        return Tool.from_code_string(tool_code)
```

## Quality Assurance Integration

### Theory Validation Pipeline

```python
class TheoryValidationPipeline:
    """Comprehensive validation of theory implementations"""
    
    validation_stages = [
        "schema_compliance",          # YAML structure validation
        "academic_source_verification", # Citation and source validation
        "concept_mapping_validation",   # MCL integration validation
        "implementation_testing",       # Tool generation and testing
        "cross_theory_consistency",     # Multi-theory integration checks
        "production_readiness"          # Performance and reliability validation
    ]
    
    async def validate_theory_production_readiness(self, theory_name: str) -> ProductionValidationResult:
        """Complete production readiness validation"""
        
        validation_results = {}
        
        for stage in self.validation_stages:
            stage_result = await getattr(self, f"_validate_{stage}")(theory_name)
            validation_results[stage] = stage_result
            
            # Fail-fast on critical issues
            if stage_result.critical_issues:
                return ProductionValidationResult(
                    status="failed",
                    failed_stage=stage,
                    results=validation_results
                )
        
        return ProductionValidationResult(
            status="production_ready",
            validation_summary=validation_results,
            recommendation="Theory ready for production deployment"
        )
```

This implementation addresses the concrete specification gaps identified in both reviews, providing the detailed technical foundation needed for theory-guided analysis in KGAS while maintaining the academic research focus and cross-modal analysis capabilities.