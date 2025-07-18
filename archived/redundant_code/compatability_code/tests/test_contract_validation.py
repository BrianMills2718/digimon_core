"""Tests for contract validation system

Tests the programmatic verification of tool contracts and compatibility.
Demonstrates automated contract validation for CI/CD integration.
"""

from pathlib import Path

# Add src to path for imports

from core.contract_validator import ContractValidator, ContractTestFramework
from core.data_models import Document, Chunk, Entity, ObjectType, QualityTier


class MockPDFLoader:
    """Mock PDF loader tool for testing contract validation"""
    
    def execute(self, file_path: str, use_ocr: bool = False, **kwargs):
        """Mock execute method that produces a Document"""
        document = Document(
            content=f"Mock content from {file_path}",
            original_filename=Path(file_path).name,
            size_bytes=1024,
            document_type="pdf",
            confidence=0.9,
            quality_tier=QualityTier.HIGH,
            created_by="T01_PDF_LOADER",
            workflow_id="test_workflow"
        )
        return {"document": document}
    
    def validate_input(self, **kwargs):
        """Validate input parameters"""
        errors = []
        if 'file_path' not in kwargs:
            errors.append("file_path is required")
        return errors
    
    def get_info(self):
        """Get tool information"""
        return {
            "name": "PDF Loader",
            "version": "1.0.0",
            "description": "Mock PDF loader for testing"
        }


class MockTextChunker:
    """Mock text chunker tool for testing contract validation"""
    
    def execute(self, document: Document, chunk_size: int = 500, 
                chunk_overlap: int = 50, **kwargs):
        """Mock execute method that produces Chunks"""
        chunks = []
        content = document.content
        
        # Simple chunking logic
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i + chunk_size]
            chunk = Chunk(
                content=chunk_content,
                document_ref=document.to_reference(),
                position=i,
                end_position=min(i + chunk_size, len(content)),
                chunk_index=len(chunks),
                confidence=document.confidence,
                quality_tier=document.quality_tier,
                created_by="T15A_TEXT_CHUNKER",
                workflow_id=document.workflow_id
            )
            chunks.append(chunk)
        
        return {"chunks": chunks}


def test_contract_validation():
    """Test contract validation functionality"""
    # Create validator
    contracts_dir = Path(__file__).parent.parent / "contracts"
    validator = ContractValidator(str(contracts_dir))
    test_framework = ContractTestFramework(validator)
    
    print("=== Contract Validation Tests ===")
    
    # Test 1: Load PDF loader contract
    print("\n1. Testing PDF Loader Contract...")
    try:
        contract = validator.load_contract("T01_PDF_LOADER")
        print(f"✓ Contract loaded: {contract['tool_id']}")
        print(f"  Category: {contract['category']}")
        print(f"  Input types: {[dt['type'] for dt in contract.get('input_contract', {}).get('required_data_types', [])]}")
        print(f"  Output types: {[dt['type'] for dt in contract.get('output_contract', {}).get('produced_data_types', [])]}")
    except Exception as e:
        print(f"✗ Failed to load contract: {e}")
    
    # Test 2: Load text chunker contract
    print("\n2. Testing Text Chunker Contract...")
    try:
        contract = validator.load_contract("T15A_TEXT_CHUNKER")
        print(f"✓ Contract loaded: {contract['tool_id']}")
        print(f"  Category: {contract['category']}")
        print(f"  Input types: {[dt['type'] for dt in contract.get('input_contract', {}).get('required_data_types', [])]}")
        print(f"  Output types: {[dt['type'] for dt in contract.get('output_contract', {}).get('produced_data_types', [])]}")
    except Exception as e:
        print(f"✗ Failed to load contract: {e}")
    
    # Test 3: Tool interface validation
    print("\n3. Testing Tool Interface Validation...")
    try:
        contract = validator.load_contract("T01_PDF_LOADER")
        pdf_loader = MockPDFLoader()
        errors = validator.validate_tool_interface(pdf_loader, contract)
        if not errors:
            print("✓ Tool interface validation passed")
        else:
            print(f"✗ Tool interface validation failed: {errors}")
    except Exception as e:
        print(f"✗ Tool interface validation error: {e}")
    
    # Test 4: Data flow validation
    print("\n4. Testing Data Flow Validation...")
    try:
        contract = validator.load_contract("T01_PDF_LOADER")
        pdf_loader = MockPDFLoader()
        
        test_input = {"file_path": "/test/sample.pdf", "use_ocr": False}
        success, errors, output = validator.validate_data_flow(pdf_loader, contract, test_input)
        
        if success:
            print("✓ Data flow validation passed")
            print(f"  Output contains: {list(output.keys())}")
        else:
            print(f"✗ Data flow validation failed: {errors}")
    except Exception as e:
        print(f"✗ Data flow validation error: {e}")
    
    # Test 5: Create test data
    print("\n5. Testing Test Data Creation...")
    try:
        test_doc = test_framework.create_test_data("Document", content="Test content")
        print(f"✓ Test document created: {test_doc.content[:50]}...")
        print(f"  Object type: {test_doc.object_type}")
        print(f"  Confidence: {test_doc.confidence}")
        
        test_chunk = test_framework.create_test_data(
            "Chunk", 
            content="Test chunk", 
            document_ref="neo4j://document/test"
        )
        print(f"✓ Test chunk created: {test_chunk.content}")
        print(f"  Document ref: {test_chunk.document_ref}")
    except Exception as e:
        print(f"✗ Test data creation failed: {e}")
    
    # Test 6: Batch validation
    print("\n6. Testing Batch Validation...")
    try:
        results = validator.batch_validate_contracts()
        summary = results['summary']
        print(f"✓ Batch validation completed")
        print(f"  Total contracts: {summary['total']}")
        print(f"  Valid contracts: {summary['valid']}")
        print(f"  Invalid contracts: {summary['invalid']}")
        
        if summary['invalid'] > 0:
            print("  Invalid contracts found:")
            for tool_id, report in results['tools'].items():
                if not report['contract_valid']:
                    print(f"    - {tool_id}: {report.get('error', 'Schema errors')}")
    except Exception as e:
        print(f"✗ Batch validation failed: {e}")
    
    print("\n=== Contract Validation Tests Complete ===")


def test_tool_chain():
    """Test validation of a tool chain"""
    print("\n=== Tool Chain Validation Test ===")
    
    try:
        contracts_dir = Path(__file__).parent.parent / "contracts"
        validator = ContractValidator(str(contracts_dir))
        
        # Create mock tools
        pdf_loader = MockPDFLoader()
        text_chunker = MockTextChunker()
        
        # Test PDF loader first
        print("1. Testing PDF Loader...")
        contract = validator.load_contract("T01_PDF_LOADER")
        test_input = {"file_path": "/test/sample.pdf"}
        success, errors, output = validator.validate_data_flow(pdf_loader, contract, test_input)
        
        if success:
            print("✓ PDF Loader validation passed")
            document = output["document"]
            print(f"  Document created: {document.original_filename}")
            
            # Test text chunker with PDF loader output
            print("\n2. Testing Text Chunker with PDF output...")
            chunker_contract = validator.load_contract("T15A_TEXT_CHUNKER")
            chunker_input = {"document": document, "chunk_size": 100}
            success, errors, output = validator.validate_data_flow(text_chunker, chunker_contract, chunker_input)
            
            if success:
                print("✓ Text Chunker validation passed")
                chunks = output["chunks"]
                print(f"  Chunks created: {len(chunks)}")
                print(f"  First chunk: {chunks[0].content[:50]}...")
            else:
                print(f"✗ Text Chunker validation failed: {errors}")
        else:
            print(f"✗ PDF Loader validation failed: {errors}")
            
    except Exception as e:
        print(f"✗ Tool chain test failed: {e}")
    
    print("\n=== Tool Chain Validation Test Complete ===")


if __name__ == "__main__":
    test_contract_validation()
    test_tool_chain()