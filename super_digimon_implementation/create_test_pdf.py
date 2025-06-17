#!/usr/bin/env python
"""Create a test research paper PDF."""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_research_paper():
    """Create a simple research paper about GraphRAG."""
    
    c = canvas.Canvas("graphrag_research_paper.pdf", pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1.5*inch, height - 1*inch, "GraphRAG: Graph Retrieval-Augmented Generation")
    
    # Authors
    c.setFont("Helvetica", 12)
    c.drawString(2*inch, height - 1.3*inch, "John Smith¹, Jane Doe², Alice Johnson¹")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(2*inch, height - 1.5*inch, "¹Stanford University, ²MIT")
    
    # Abstract
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 2*inch, "Abstract")
    
    c.setFont("Helvetica", 10)
    text = [
        "This paper introduces GraphRAG, a novel approach to retrieval-augmented generation",
        "that leverages knowledge graphs. Microsoft Research pioneered early work in this area,",
        "while Google DeepMind explored alternative approaches. Our method combines Neo4j",
        "graph databases with FAISS vector search to enable complex multi-hop reasoning.",
        "",
        "We demonstrate that GraphRAG outperforms traditional RAG systems on knowledge-",
        "intensive tasks. OpenAI's GPT-4 serves as our base language model. The system",
        "was tested on datasets from Wikipedia and scientific papers."
    ]
    
    y = height - 2.3*inch
    for line in text:
        c.drawString(1*inch, y, line)
        y -= 14
    
    # Introduction
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y - 0.3*inch, "1. Introduction")
    
    c.setFont("Helvetica", 10)
    y -= 0.5*inch
    intro_text = [
        "Retrieval-augmented generation (RAG) has emerged as a powerful paradigm for",
        "enhancing language models. Facebook AI Research (now Meta AI) introduced the",
        "original RAG paper in 2020. Since then, companies like Anthropic and Google have",
        "developed their own variants.",
        "",
        "Traditional RAG systems rely on dense retrieval from vector databases. However,",
        "they struggle with multi-hop reasoning and complex relationships. GraphRAG addresses",
        "these limitations by incorporating structured knowledge graphs.",
        "",
        "Our contributions include:",
        "• A novel graph construction algorithm that extracts entities and relationships",
        "• Integration with PageRank for importance-based retrieval",
        "• Evaluation on three benchmark datasets"
    ]
    
    for line in intro_text:
        c.drawString(1*inch, y, line)
        y -= 14
    
    # Methods
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y - 0.3*inch, "2. Methods")
    
    c.setFont("Helvetica", 10)
    y -= 0.5*inch
    methods_text = [
        "GraphRAG operates in four phases:",
        "",
        "2.1 Entity Extraction: We use spaCy NER to identify entities. Microsoft, Google,",
        "and other organizations are extracted as ORG entities. Persons like Elon Musk",
        "and Sam Altman are identified as PERSON entities.",
        "",
        "2.2 Relationship Extraction: Our system identifies relationships such as 'founded',",
        "'acquired', and 'competes with'. For example, 'Microsoft invested $10 billion in",
        "OpenAI' yields an INVESTED_IN relationship.",
        "",
        "2.3 Graph Construction: Entities become nodes in Neo4j, while relationships form",
        "edges. We tested on graphs with over 1 million nodes from Wikidata.",
        "",
        "2.4 Query Processing: Natural language queries are processed through our pipeline.",
        "Complex queries like 'Which companies did Google acquire?' leverage graph traversal."
    ]
    
    for line in methods_text:
        if y < 1*inch:
            c.showPage()  # New page
            y = height - 1*inch
            c.setFont("Helvetica", 10)
        c.drawString(1*inch, y, line)
        y -= 14
    
    # Save
    c.save()
    print("Created: graphrag_research_paper.pdf")

if __name__ == "__main__":
    create_research_paper()