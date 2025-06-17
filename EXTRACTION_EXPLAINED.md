# How Entity and Relationship Extraction Works

## Overview

The Super-Digimon system extracts entities and relationships from text using a two-stage pipeline:

1. **Entity Extraction (T23a)** - Identifies named entities like people, organizations, and locations
2. **Relationship Extraction (T27)** - Finds connections between those entities

## Stage 1: Entity Extraction with spaCy NER

### What is spaCy?
spaCy is a popular NLP library with pre-trained machine learning models for various languages. We use the English model (`en_core_web_sm`) which has been trained on millions of documents to recognize named entities.

### How it Works

1. **Text Processing**: The input text is processed through spaCy's pipeline:
   ```
   "Elon Musk founded Tesla in 2003" 
   → tokenization → part-of-speech tagging → dependency parsing → NER
   ```

2. **Entity Recognition**: The model identifies spans of text as entities:
   - "Elon Musk" → PERSON
   - "Tesla" → ORG  
   - "2003" → DATE

3. **Entity Types We Extract**:
   - **PERSON**: People, characters (e.g., "Steve Jobs", "Barack Obama")
   - **ORG**: Companies, institutions (e.g., "Apple Inc.", "MIT")
   - **GPE**: Geopolitical entities (e.g., "United States", "California") 
   - **PRODUCT**: Products, services (e.g., "iPhone", "Windows")
   - **EVENT**: Named events (e.g., "World War II", "Olympics")
   - **WORK_OF_ART**: Titles of creative works (e.g., "Mona Lisa")
   - **LAW**: Laws, acts (e.g., "Constitution", "GDPR")
   - **LANGUAGE**: Languages (e.g., "English", "Python")
   - **FACILITY**: Buildings, infrastructure (e.g., "Golden Gate Bridge")
   - **MONEY**: Monetary values (e.g., "$100 million")
   - **DATE**: Dates, periods (e.g., "2023", "last year")
   - **TIME**: Times (e.g., "3:00 PM", "morning")

4. **Confidence Scoring**: Each entity gets a confidence score based on:
   - Base confidence: 0.85 (spaCy is generally reliable)
   - Entity type adjustments (MONEY/DATE are more reliable: 0.95)
   - Entity length (longer entities are more confident)
   - Context quality from the source document

### Example Output
```python
Input: "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976."

Entities:
- "Apple Inc." (ORG, confidence: 0.87)
- "Steve Jobs" (PERSON, confidence: 0.89)
- "Cupertino" (GPE, confidence: 0.83)
- "California" (GPE, confidence: 0.85)
- "1976" (DATE, confidence: 0.95)
```

## Stage 2: Relationship Extraction

### Three Methods (in order of preference)

#### 1. Pattern-Based Extraction (Most Reliable)

Uses predefined linguistic patterns to find relationships:

**Example Patterns**:
- **Ownership**: "X owns Y", "X has Y", "X's Y"
  - "Elon Musk owns Twitter" → (Elon Musk)-[OWNS]->(Twitter)
  
- **Employment**: "X works at Y", "X CEO of Y", "X employed by Y"
  - "Tim Cook is CEO of Apple" → (Tim Cook)-[WORKS_FOR]->(Apple)
  
- **Location**: "X located in Y", "X based in Y", "X headquarters in Y"
  - "Google is based in Mountain View" → (Google)-[LOCATED_IN]->(Mountain View)
  
- **Creation**: "X founded Y", "X created Y", "X established Y"
  - "Bill Gates founded Microsoft" → (Bill Gates)-[CREATED]->(Microsoft)

**Confidence**: 0.7-0.9 (patterns are quite reliable)

#### 2. Dependency Parsing (Grammatical Analysis)

Uses spaCy's dependency parser to understand sentence structure:

```
"Steve Jobs founded Apple"
      ↓        ↓       ↓
   SUBJECT   VERB   OBJECT
```

The system:
1. Finds subject-verb-object triples
2. Matches entities to subjects/objects
3. Maps verbs to relationship types:
   - "founded/created/established" → CREATED
   - "owns/has/possesses" → OWNS
   - "leads/manages/heads" → LEADS

**Confidence**: 0.6-0.8 (depends on sentence complexity)

#### 3. Proximity-Based (Fallback)

When no patterns match, looks for entities near each other:

- Entities within 50 characters
- Connected by words like "and", "with", "of"
- Creates generic RELATED_TO relationships

Example: "Microsoft and OpenAI announced..." → (Microsoft)-[RELATED_TO]->(OpenAI)

**Confidence**: 0.5 (lowest confidence method)

### Confidence Calculation

Final confidence combines:
- Pattern/method confidence (40% weight)
- Context confidence (30% weight)  
- Entity confidence (30% weight)

## Complete Example

**Input Text**:
```
"Elon Musk is the CEO of Tesla, which is headquartered in Austin, Texas. 
He also founded SpaceX in 2002. Both companies are leaders in their industries."
```

**Step 1 - Entity Extraction**:
- Elon Musk (PERSON)
- Tesla (ORG)
- Austin (GPE)
- Texas (GPE)
- SpaceX (ORG)
- 2002 (DATE)

**Step 2 - Relationship Extraction**:

1. Pattern matching finds:
   - "Elon Musk is the CEO of Tesla" → (Elon Musk)-[WORKS_FOR]->(Tesla)
   - "Tesla...headquartered in Austin, Texas" → (Tesla)-[LOCATED_IN]->(Austin)
   - "He also founded SpaceX" → (Elon Musk)-[CREATED]->(SpaceX)

2. Proximity finds:
   - "Austin, Texas" → (Austin)-[LOCATED_IN]->(Texas)

**Final Graph**:
```
Elon Musk --[WORKS_FOR]--> Tesla
Elon Musk --[CREATED]--> SpaceX  
Tesla --[LOCATED_IN]--> Austin
Austin --[LOCATED_IN]--> Texas
```

## Why This Approach?

1. **Reliability**: Pattern-based extraction is highly accurate for common relationships
2. **Flexibility**: Multiple methods catch different relationship types
3. **Transparency**: Easy to understand why a relationship was extracted
4. **Performance**: Fast enough for real-time processing
5. **Extensibility**: Easy to add new patterns and relationship types

## Limitations

1. **Language Dependency**: Only works with English text
2. **Pattern Coverage**: Can't extract relationships not covered by patterns
3. **Context Understanding**: Doesn't understand complex reasoning or implications
4. **Coreference**: Doesn't resolve pronouns (e.g., "he", "it", "they")
5. **Negation**: Doesn't handle negative statements well

## Viewing the Results

The extracted entities and relationships are stored in Neo4j as a knowledge graph. You can:

1. Query specific entities and their connections
2. Calculate importance using PageRank
3. Traverse multi-hop paths to answer questions
4. Visualize the graph structure

The confidence scores help you understand which extractions are most reliable.