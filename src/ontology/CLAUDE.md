# Ontology Module - CLAUDE.md

## Overview
The `src/ontology/` directory contains **domain ontology generation** tools that create structured knowledge frameworks from conversations and domain descriptions. These tools use LLM-based generation to create domain-specific ontologies for entity and relationship extraction.

## Ontology Architecture

### Generator Pattern
Ontology tools follow a structured generation pattern:
- **GeminiOntologyGenerator**: OpenAI o3-mini based ontology generation
- **Structured Output**: JSON-based structured ontology generation
- **Domain-Specific**: Focus on domain-specific entity and relationship types
- **Validation**: Built-in ontology validation and refinement

### LLM Integration Pattern
All ontology generators integrate with LLMs:
- **OpenAI Integration**: Use OpenAI o3-mini for generation
- **Structured Prompts**: Create structured prompts for consistent output
- **JSON Response**: Use JSON response format for structured parsing
- **Error Handling**: Robust error handling for LLM responses

## Individual Tool Patterns

### GeminiOntologyGenerator (`gemini_ontology_generator.py`)
**Purpose**: Generate domain ontologies using OpenAI o3-mini with structured output

**Key Patterns**:
- **Conversation-Based**: Generate ontologies from conversation history
- **Structured Output**: Use JSON format for consistent parsing
- **Domain-Specific**: Focus on domain-specific types, not generic ones
- **Validation**: Built-in ontology validation and refinement

**Usage**:
```python
from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator

generator = GeminiOntologyGenerator(api_key="your-openai-key")

# Generate from conversation
messages = [
    {"role": "user", "content": "Tell me about machine learning algorithms"},
    {"role": "assistant", "content": "Machine learning includes supervised, unsupervised, and reinforcement learning..."}
]

ontology = generator.generate_from_conversation(
    messages=messages,
    temperature=0.7,
    constraints={"max_entities": 10, "max_relations": 15}
)

print(f"Domain: {ontology.domain_name}")
print(f"Entity Types: {len(ontology.entity_types)}")
print(f"Relationship Types: {len(ontology.relationship_types)}")
```

**Core Components**:

#### Conversation Processing
```python
def generate_from_conversation(self, messages: List[Dict[str, str]], 
                             temperature: float = 0.7,
                             constraints: Optional[Dict[str, Any]] = None) -> DomainOntology:
    """Generate ontology from conversation history"""
```

**Processing Features**:
- **Message Formatting**: Format conversation messages into text
- **Constraint Handling**: Apply generation constraints
- **Prompt Creation**: Create structured prompts for LLM
- **Response Parsing**: Parse structured JSON responses

#### Structured Prompt Creation
```python
def _create_ontology_prompt(self, conversation: str, 
                           constraints: Optional[Dict[str, Any]] = None) -> str:
    """Create structured prompt for ontology generation"""
```

**Prompt Structure**:
- **Conversation Context**: Include full conversation history
- **Constraints**: Apply user-specified constraints
- **JSON Format**: Specify exact JSON output format
- **Requirements**: Include specific naming and content requirements

**Prompt Requirements**:
- **Entity Types**: UPPERCASE_WITH_UNDERSCORES naming
- **Relationship Types**: UPPERCASE_WITH_UNDERSCORES naming
- **Examples**: 3-5 concrete examples for each type
- **Domain Focus**: Domain-specific types, not generic ones
- **Guidelines**: Helpful identification guidelines

#### Robust JSON Parsing
```python
def _parse_response(self, response_text: str) -> Dict[str, Any]:
    """Parse JSON response with robust error handling"""
```

**Parsing Strategies**:
- **Direct Parsing**: Try direct JSON parsing first
- **JSON Extraction**: Extract JSON from text with extra content
- **JSON Fixing**: Fix common JSON issues automatically
- **Error Logging**: Log all parsing attempts and errors

**JSON Cleaning**:
```python
def _clean_json_response(self, response_text: str) -> str:
    """Clean response text to extract JSON content"""
```

**Cleaning Features**:
- **Markdown Removal**: Remove markdown code blocks
- **Whitespace Cleaning**: Clean extra whitespace
- **Character Encoding**: Handle encoding issues
- **Format Normalization**: Normalize JSON format

#### Ontology Building
```python
def _build_ontology(self, data: Dict[str, Any], conversation: str) -> DomainOntology:
    """Convert parsed data to DomainOntology object"""
```

**Building Features**:
- **Data Validation**: Validate parsed data structure
- **Object Creation**: Create DomainOntology objects
- **Type Conversion**: Convert data types appropriately
- **Metadata Addition**: Add generation metadata

#### Ontology Validation
```python
def validate_ontology(self, ontology: DomainOntology, sample_text: str) -> Dict[str, Any]:
    """Validate ontology against sample text"""
```

**Validation Features**:
- **Coverage Analysis**: Check entity and relationship coverage
- **Example Testing**: Test examples against sample text
- **Guideline Testing**: Test identification guidelines
- **Quality Assessment**: Assess ontology quality

#### Ontology Refinement
```python
def refine_ontology(self, ontology: DomainOntology, 
                   refinement_request: str) -> DomainOntology:
    """Refine ontology based on feedback"""
```

**Refinement Features**:
- **Feedback Integration**: Integrate user feedback
- **Incremental Updates**: Update ontology incrementally
- **Quality Improvement**: Improve ontology quality
- **Validation**: Validate refined ontology

## Data Models

### DomainOntology
```python
@dataclass
class DomainOntology:
    domain_name: str
    domain_description: str
    entity_types: List[EntityType]
    relationship_types: List[RelationshipType]
    identification_guidelines: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### EntityType
```python
@dataclass
class EntityType:
    name: str  # UPPERCASE_WITH_UNDERSCORES
    description: str
    examples: List[str]
    attributes: List[str]
```

### RelationshipType
```python
@dataclass
class RelationshipType:
    name: str  # UPPERCASE_WITH_UNDERSCORES
    description: str
    source_types: List[str]
    target_types: List[str]
    examples: List[str]
```

## Common Commands & Workflows

### Development Commands
```bash
# Test ontology generator
python -c "from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator; print(GeminiOntologyGenerator.__doc__)"

# Test with mock conversation
python -c "from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator; import os; os.environ['OPENAI_API_KEY'] = 'test'; print(GeminiOntologyGenerator()._format_conversation([{'role': 'user', 'content': 'test'}]))"

# Test prompt creation
python -c "from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator; import os; os.environ['OPENAI_API_KEY'] = 'test'; gen = GeminiOntologyGenerator(); print(gen._create_ontology_prompt('test conversation', {'max_entities': 5}))"
```

### Testing Commands
```bash
# Test JSON parsing
python -c "from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator; import os; os.environ['OPENAI_API_KEY'] = 'test'; gen = GeminiOntologyGenerator(); print(gen._clean_json_response('```json\n{\"test\": \"value\"}\n```'))"

# Test ontology validation
python -c "from src.ontology import DomainOntology; from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator; import os; os.environ['OPENAI_API_KEY'] = 'test'; gen = GeminiOntologyGenerator(); print(gen.validate_ontology.__doc__)"

# Test ontology refinement
python -c "from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator; import os; os.environ['OPENAI_API_KEY'] = 'test'; gen = GeminiOntologyGenerator(); print(gen.refine_ontology.__doc__)"
```

### Debugging Commands
```bash
# Check API key configuration
python -c "import os; print(f'OpenAI API Key: {os.getenv(\"OPENAI_API_KEY\", \"Not set\")[:10]}...' if os.getenv(\"OPENAI_API_KEY\") else 'Not set')"

# Test model configuration
python -c "from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator; import os; os.environ['OPENAI_API_KEY'] = 'test'; gen = GeminiOntologyGenerator(); print(f'Model: {gen.model}')"

# Test conversation formatting
python -c "from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator; import os; os.environ['OPENAI_API_KEY'] = 'test'; gen = GeminiOntologyGenerator(); messages = [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi there!'}]; print(gen._format_conversation(messages))"
```

## Code Style & Conventions

### Generator Design Patterns
- **Single Responsibility**: Each generator has one clear purpose
- **LLM Integration**: Consistent LLM integration patterns
- **Structured Output**: Use structured output for consistency
- **Error Handling**: Robust error handling for LLM responses

### Naming Conventions
- **Generator Names**: Use `Generator` suffix for generator classes
- **Method Names**: Use descriptive names for generation methods
- **Variable Names**: Use descriptive names for parameters
- **Constants**: Use UPPER_CASE for magic numbers and thresholds

### Error Handling Patterns
- **LLM Error Handling**: Handle LLM API errors gracefully
- **JSON Parsing**: Multiple strategies for JSON parsing
- **Validation Errors**: Handle validation errors with context
- **API Errors**: Handle API key and connectivity errors

### Logging Patterns
- **Generation Logging**: Log generation progress and results
- **Error Logging**: Log errors with context and recovery attempts
- **Validation Logging**: Log validation results and issues
- **Performance Logging**: Log generation timing and metrics

## Integration Points

### LLM Integration
- **OpenAI API**: Integration with OpenAI o3-mini model
- **Structured Prompts**: Create structured prompts for consistent output
- **JSON Response**: Use JSON response format for structured parsing
- **Error Handling**: Handle LLM API errors and timeouts

### Core Integration
- **DomainOntology**: Integration with core ontology data models
- **EntityType**: Integration with entity type definitions
- **RelationshipType**: Integration with relationship type definitions
- **Validation**: Integration with ontology validation

### External Dependencies
- **OpenAI**: OpenAI API client for LLM access
- **JSON**: Standard JSON parsing and serialization
- **Dataclasses**: Structured data models
- **Logging**: Standard Python logging

## Performance Considerations

### LLM Optimization
- **Prompt Optimization**: Optimize prompts for efficiency
- **Response Caching**: Cache LLM responses when possible
- **Batch Processing**: Process multiple requests efficiently
- **Rate Limiting**: Handle API rate limits gracefully

### Memory Management
- **Response Streaming**: Stream large responses efficiently
- **Object Reuse**: Reuse objects when possible
- **Cleanup**: Proper cleanup of temporary data
- **Memory Monitoring**: Monitor memory usage during generation

### Speed Optimization
- **Parallel Processing**: Process multiple ontologies in parallel
- **Caching**: Cache generated ontologies
- **Incremental Updates**: Update ontologies incrementally
- **Lazy Loading**: Load data only when needed

## Testing Patterns

### Unit Testing
- **Generator Isolation**: Test each generator independently
- **Method Testing**: Test individual generation methods
- **Parsing Testing**: Test JSON parsing strategies
- **Validation Testing**: Test ontology validation

### Integration Testing
- **LLM Integration**: Test LLM integration with mock responses
- **API Integration**: Test API key and connectivity
- **Data Model Integration**: Test data model integration
- **End-to-End**: Test complete generation pipeline

### Mock Testing
- **LLM Mocking**: Mock LLM responses for testing
- **API Mocking**: Mock API calls for testing
- **Error Mocking**: Mock error conditions for testing
- **Performance Mocking**: Mock performance characteristics

## Troubleshooting

### Common Issues
1. **API Key Issues**: Check OpenAI API key configuration
2. **JSON Parsing Issues**: Check JSON response format
3. **LLM Errors**: Handle LLM API errors and timeouts
4. **Validation Issues**: Check ontology validation criteria

### Debug Commands
```bash
# Check API connectivity
python -c "from openai import OpenAI; import os; client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('API connectivity test')"

# Test JSON parsing
python -c "import json; test_json = '{\"test\": \"value\"}'; print(json.loads(test_json))"

# Test ontology data models
python -c "from src.ontology import DomainOntology, EntityType, RelationshipType; print('Data models imported successfully')"
```

## Migration & Upgrades

### LLM Model Migration
- **Model Updates**: Update to newer LLM models
- **API Changes**: Handle API changes and deprecations
- **Prompt Updates**: Update prompts for new models
- **Response Format**: Handle response format changes

### Data Model Migration
- **Ontology Migration**: Migrate ontology data models
- **Entity Type Migration**: Migrate entity type definitions
- **Relationship Migration**: Migrate relationship type definitions
- **Validation Migration**: Migrate validation rules

### Configuration Updates
- **API Configuration**: Update API configuration
- **Model Configuration**: Update model configuration
- **Prompt Configuration**: Update prompt templates
- **Validation Configuration**: Update validation rules 