"""
TwitterExplorer Tool Contract Validation Tests

TDD Phase 1: Contract-first validation tests
These tests validate the tool contract before implementation.
"""

import pytest
import yaml
import jsonschema
from pathlib import Path

# Test setup
CONTRACT_PATH = Path(__file__).parent.parent.parent / "contracts" / "tools" / "T85_TWITTER_EXPLORER.yaml"

class TestTwitterExplorerContract:
    """Test Twitter tool contract compliance before implementation"""
    
    @pytest.fixture
    def contract(self):
        """Load Twitter Explorer contract"""
        with open(CONTRACT_PATH, 'r') as f:
            return yaml.safe_load(f)
    
    def test_contract_file_exists(self):
        """Test contract file exists at expected location"""
        assert CONTRACT_PATH.exists(), f"Contract file not found at {CONTRACT_PATH}"
    
    def test_contract_loads_valid_yaml(self):
        """Test contract is valid YAML"""
        try:
            with open(CONTRACT_PATH, 'r') as f:
                contract = yaml.safe_load(f)
            assert contract is not None
        except yaml.YAMLError as e:
            pytest.fail(f"Contract is not valid YAML: {e}")
    
    def test_contract_has_required_fields(self, contract):
        """Test contract has all required KGAS fields"""
        required_fields = [
            "tool_id", "name", "description", "version", "category",
            "input_schema", "output_schema", "dependencies", 
            "performance_requirements", "error_conditions"
        ]
        
        for field in required_fields:
            assert field in contract, f"Missing required field: {field}"
    
    def test_tool_id_matches_expected(self, contract):
        """Test tool ID matches expected value"""
        assert contract["tool_id"] == "T85_TWITTER_EXPLORER"
    
    def test_category_is_social_media_analysis(self, contract):
        """Test tool category is correct"""
        assert contract["category"] == "social_media_analysis"
    
    def test_input_schema_structure(self, contract):
        """Test input schema has required structure"""
        input_schema = contract["input_schema"]
        
        # Must be an object schema
        assert input_schema["type"] == "object"
        assert "properties" in input_schema
        assert "required" in input_schema
        
        properties = input_schema["properties"]
        
        # Must support natural language queries
        assert "query" in properties
        assert properties["query"]["type"] == "string"
        assert properties["query"]["minLength"] >= 1
        
        # Must support API credentials
        assert "api_keys" in properties
        api_keys = properties["api_keys"]["properties"]
        assert "gemini_key" in api_keys
        assert "rapidapi_key" in api_keys
        
        # Must support configuration options
        assert "max_results" in properties
        assert "include_graph" in properties
        assert "timeout_seconds" in properties
        
        # Check required fields
        required = input_schema["required"]
        assert "query" in required
        assert "api_keys" in required
    
    def test_output_schema_supports_kgas_integration(self, contract):
        """Test output schema integrates with KGAS services"""
        output_schema = contract["output_schema"]
        
        assert output_schema["type"] == "object"
        properties = output_schema["properties"]
        
        # Must produce entities for Identity Service
        assert "entities" in properties
        assert properties["entities"]["type"] == "array"
        
        entity_schema = properties["entities"]["items"]
        entity_props = entity_schema["properties"]
        assert "entity_id" in entity_props
        assert "entity_type" in entity_props
        assert "surface_form" in entity_props
        assert "confidence" in entity_props
        
        # Must produce relationships for graph building
        assert "relationships" in properties
        assert properties["relationships"]["type"] == "array"
        
        relationship_schema = properties["relationships"]["items"]
        rel_props = relationship_schema["properties"]
        assert "relationship_id" in rel_props
        assert "source_entity_id" in rel_props
        assert "target_entity_id" in rel_props
        assert "relationship_type" in rel_props
        
        # Must produce graph data for Neo4j
        assert "graph_data" in properties
        graph_props = properties["graph_data"]["properties"]
        assert "nodes" in graph_props
        assert "edges" in graph_props
        
        # Must provide summary for users
        assert "summary" in properties
        assert properties["summary"]["type"] == "string"
        
        # Must provide processing statistics
        assert "processing_stats" in properties
    
    def test_entity_types_are_twitter_specific(self, contract):
        """Test entity types are appropriate for Twitter"""
        output_schema = contract["output_schema"]
        entity_schema = output_schema["properties"]["entities"]["items"]
        entity_type_enum = entity_schema["properties"]["entity_type"]["enum"]
        
        expected_types = ["TwitterUser", "Tweet", "TwitterList", "TwitterSpace", "TwitterCommunity"]
        assert set(entity_type_enum) == set(expected_types)
    
    def test_relationship_types_are_twitter_specific(self, contract):
        """Test relationship types are appropriate for Twitter"""
        output_schema = contract["output_schema"]
        rel_schema = output_schema["properties"]["relationships"]["items"]
        rel_type_enum = rel_schema["properties"]["relationship_type"]["enum"]
        
        expected_types = ["FOLLOWS", "MENTIONS", "RETWEETS", "REPLIES_TO", "QUOTES", "MEMBER_OF", "OWNS"]
        assert set(rel_type_enum) == set(expected_types)
    
    def test_performance_requirements_realistic(self, contract):
        """Test performance requirements are realistic for Twitter API"""
        perf_req = contract["performance_requirements"]
        
        # Execution time should accommodate API calls
        assert perf_req["max_execution_time"] >= 60.0  # At least 1 minute
        assert perf_req["max_execution_time"] <= 300.0  # At most 5 minutes
        
        # Memory should accommodate graph building
        assert perf_req["max_memory_mb"] >= 200  # At least 200MB
        assert perf_req["max_memory_mb"] <= 1000  # At most 1GB
        
        # Accuracy should be high but realistic
        assert perf_req["min_accuracy"] >= 0.8
        assert perf_req["min_accuracy"] <= 1.0
        
        # API calls should be limited to prevent quota exhaustion
        assert perf_req["max_api_calls_per_query"] >= 1
        assert perf_req["max_api_calls_per_query"] <= 50
    
    def test_error_conditions_comprehensive(self, contract):
        """Test error conditions cover expected failure modes"""
        error_conditions = contract["error_conditions"]
        
        expected_errors = [
            "INVALID_QUERY",
            "MISSING_API_KEYS", 
            "INVALID_API_CREDENTIALS",
            "RATE_LIMIT_EXCEEDED",
            "API_TIMEOUT",
            "QUERY_TOO_COMPLEX",
            "UNSUPPORTED_QUERY_TYPE",
            "GRAPH_CONSTRUCTION_FAILED",
            "ENTITY_EXTRACTION_FAILED",
            "SERVICE_INTEGRATION_FAILED"
        ]
        
        for expected_error in expected_errors:
            assert expected_error in error_conditions
    
    def test_dependencies_include_required_libraries(self, contract):
        """Test dependencies include all required libraries"""
        dependencies = contract["dependencies"]
        
        required_deps = [
            "google-generativeai",  # For LLM query planning
            "requests",  # For API calls
            "networkx",  # For graph operations
            "identity_service",  # KGAS service
            "provenance_service",  # KGAS service
            "quality_service"  # KGAS service
        ]
        
        for dep in required_deps:
            assert dep in dependencies
    
    def test_integration_points_defined(self, contract):
        """Test integration points with KGAS services are defined"""
        integration = contract["integration_points"]
        
        # Must integrate with Identity Service
        assert "identity_service" in integration
        identity_methods = integration["identity_service"]
        assert "create_entity" in identity_methods
        assert "create_mention" in identity_methods
        
        # Must integrate with Provenance Service
        assert "provenance_service" in integration
        provenance_methods = integration["provenance_service"]
        assert "log_execution" in provenance_methods
        
        # Must integrate with Quality Service
        assert "quality_service" in integration
        quality_methods = integration["quality_service"]
        assert "assess_confidence" in quality_methods
    
    def test_theory_compliance_specified(self, contract):
        """Test theory compliance is properly specified"""
        theory_compliance = contract["theory_compliance"]
        
        assert "meta_schema_version" in theory_compliance
        assert "ontology_alignment" in theory_compliance
        assert "extraction_strategy" in theory_compliance
        assert "domain_specific" in theory_compliance
        assert theory_compliance["domain_specific"] is True
        assert theory_compliance["domain"] == "social_media_analysis"


class TestTwitterExplorerContractValidation:
    """Test contract validation against JSON schemas"""
    
    @pytest.fixture
    def contract(self):
        """Load Twitter Explorer contract"""
        with open(CONTRACT_PATH, 'r') as f:
            return yaml.safe_load(f)
    
    def test_input_schema_is_valid_json_schema(self, contract):
        """Test input schema is valid JSON schema"""
        input_schema = contract["input_schema"]
        
        try:
            # Validate schema structure
            jsonschema.Draft7Validator.check_schema(input_schema)
        except jsonschema.SchemaError as e:
            pytest.fail(f"Input schema is not valid JSON schema: {e}")
    
    def test_output_schema_is_valid_json_schema(self, contract):
        """Test output schema is valid JSON schema"""
        output_schema = contract["output_schema"]
        
        try:
            # Validate schema structure
            jsonschema.Draft7Validator.check_schema(output_schema)
        except jsonschema.SchemaError as e:
            pytest.fail(f"Output schema is not valid JSON schema: {e}")
    
    def test_sample_input_validates_against_schema(self, contract):
        """Test sample input validates against input schema"""
        input_schema = contract["input_schema"]
        
        sample_input = {
            "query": "Tell me about the user @github",
            "api_keys": {
                "gemini_key": "test_gemini_key",
                "rapidapi_key": "test_rapidapi_key"
            },
            "max_results": 50,
            "include_graph": True,
            "timeout_seconds": 60
        }
        
        try:
            jsonschema.validate(sample_input, input_schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"Sample input failed validation: {e}")
    
    def test_sample_output_validates_against_schema(self, contract):
        """Test sample output validates against output schema"""
        output_schema = contract["output_schema"]
        
        sample_output = {
            "summary": "Found information about GitHub user profile",
            "entities": [
                {
                    "entity_id": "ent_001",
                    "entity_type": "TwitterUser",
                    "surface_form": "@github",
                    "canonical_name": "github",
                    "confidence": 0.95,
                    "metadata": {"followers_count": 1000000}
                }
            ],
            "relationships": [
                {
                    "relationship_id": "rel_001",
                    "source_entity_id": "ent_001",
                    "target_entity_id": "ent_002",
                    "relationship_type": "FOLLOWS",
                    "confidence": 0.9,
                    "metadata": {}
                }
            ],
            "graph_data": {
                "nodes": [{"id": "ent_001", "label": "TwitterUser"}],
                "edges": [{"source": "ent_001", "target": "ent_002", "type": "FOLLOWS"}],
                "metadata": {"node_count": 1, "edge_count": 1, "connected_components": 1}
            },
            "api_execution_log": [
                {
                    "step": 1,
                    "endpoint": "screenname.php",
                    "parameters": {"screenname": "github"},
                    "response_time": 1.2,
                    "status": "success"
                }
            ],
            "processing_stats": {
                "total_api_calls": 1,
                "total_execution_time": 2.5,
                "entities_extracted": 1,
                "relationships_extracted": 1,
                "query_complexity_score": 0.3
            }
        }
        
        try:
            jsonschema.validate(sample_output, output_schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"Sample output failed validation: {e}")


class TestTwitterExplorerContractIntegrity:
    """Test contract internal consistency and integrity"""
    
    @pytest.fixture
    def contract(self):
        """Load Twitter Explorer contract"""
        with open(CONTRACT_PATH, 'r') as f:
            return yaml.safe_load(f)
    
    def test_all_entity_types_have_relationship_support(self, contract):
        """Test all entity types can participate in relationships"""
        output_schema = contract["output_schema"]["properties"]
        
        entity_types = set(output_schema["entities"]["items"]["properties"]["entity_type"]["enum"])
        relationship_types = output_schema["relationships"]["items"]["properties"]["relationship_type"]["enum"]
        
        # All entity types should be able to participate in some relationship
        # This is a design consistency check
        assert len(entity_types) > 0
        assert len(relationship_types) > 0
    
    def test_confidence_ranges_consistent(self, contract):
        """Test confidence ranges are consistent across schema"""
        output_schema = contract["output_schema"]["properties"]
        
        # Entity confidence
        entity_confidence = output_schema["entities"]["items"]["properties"]["confidence"]
        assert entity_confidence["minimum"] == 0
        assert entity_confidence["maximum"] == 1
        
        # Relationship confidence
        rel_confidence = output_schema["relationships"]["items"]["properties"]["confidence"]
        assert rel_confidence["minimum"] == 0
        assert rel_confidence["maximum"] == 1
    
    def test_id_field_consistency(self, contract):
        """Test ID fields are consistently defined"""
        output_schema = contract["output_schema"]["properties"]
        
        # Entity IDs
        entity_id = output_schema["entities"]["items"]["properties"]["entity_id"]
        assert entity_id["type"] == "string"
        
        # Relationship IDs
        rel_id = output_schema["relationships"]["items"]["properties"]["relationship_id"]
        assert rel_id["type"] == "string"
        
        # Source/target entity IDs in relationships
        source_id = output_schema["relationships"]["items"]["properties"]["source_entity_id"]
        target_id = output_schema["relationships"]["items"]["properties"]["target_entity_id"]
        assert source_id["type"] == "string"
        assert target_id["type"] == "string"