**Doc status**: Living – auto-checked by doc-governance CI

# Third-Party Licenses

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Purpose**: Third-party licenses and attributions for KGAS dependencies

---

## Ontology Licenses

### DOLCE
- **License**: CC-BY 4.0
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: http://www.ontologydesignpatterns.org/ont/dul/DUL.owl

### FOAF
- **License**: CC-BY 1.0
- **Usage**: Attribution required
- **Attribution**: Required
- **Source**: http://xmlns.com/foaf/spec/

### SIOC
- **License**: W3C Document Licence
- **Usage**: Attribution required
- **Attribution**: Required
- **Source**: http://rdfs.org/sioc/spec/

---

## Software Dependencies

### Python Libraries

#### Core Dependencies
- **pandas**: BSD 3-Clause License
- **numpy**: BSD 3-Clause License
- **scikit-learn**: BSD 3-Clause License
- **pydantic**: MIT License
- **click**: BSD 3-Clause License

#### NLP Dependencies
- **spacy**: MIT License
- **transformers**: Apache 2.0 License
- **sentence-transformers**: Apache 2.0 License
- **nltk**: Apache 2.0 License

#### Graph Dependencies
- **neo4j**: Apache 2.0 License
- **networkx**: BSD 3-Clause License
- **rdflib**: BSD 3-Clause License

#### ML Dependencies
- **torch**: BSD 3-Clause License
- **tensorflow**: Apache 2.0 License
- **scipy**: BSD 3-Clause License

#### Utility Dependencies
- **rich**: MIT License
- **typer**: MIT License
- **fastapi**: MIT License
- **uvicorn**: BSD 3-Clause License

---

## Database Licenses

### Neo4j
- **License**: GPL v3 (Community Edition)
- **Usage**: Open source use
- **Commercial**: Requires commercial license
- **Source**: https://neo4j.com/

### PostgreSQL
- **License**: PostgreSQL License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://www.postgresql.org/

---

## Model Licenses

### OpenAI Models
- **GPT-4**: OpenAI Terms of Service
- **text-embedding-3-large**: OpenAI Terms of Service
- **Usage**: Requires OpenAI API key
- **Commercial**: Subject to OpenAI pricing

### Google Models
- **Gemini**: Google AI Terms of Service
- **Usage**: Requires Google API key
- **Commercial**: Subject to Google pricing

### Hugging Face Models
- **BERT**: Apache 2.0 License
- **RoBERTa**: MIT License
- **DistilBERT**: Apache 2.0 License
- **Usage**: Commercial use OK with attribution

---

## UI Framework Licenses

### Streamlit
- **License**: Apache 2.0 License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://streamlit.io/

### React (if used)
- **License**: MIT License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://reactjs.org/

---

## Development Tools

### Docker
- **License**: Apache 2.0 License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://www.docker.com/

### Git
- **License**: GPL v2
- **Usage**: Open source use
- **Commercial**: Commercial use OK
- **Source**: https://git-scm.com/

### Python
- **License**: PSF License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://www.python.org/

---

## Testing Framework Licenses

### pytest
- **License**: MIT License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://pytest.org/

### coverage
- **License**: Apache 2.0 License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://coverage.readthedocs.io/

---

## Documentation Tools

### Sphinx
- **License**: BSD 2-Clause License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://www.sphinx-doc.org/

### MkDocs
- **License**: BSD 2-Clause License
- **Usage**: Commercial use OK
- **Attribution**: Required
- **Source**: https://www.mkdocs.org/

---

## License Compliance

### Attribution Requirements
All third-party components require proper attribution in:
- **README.md**: List of major dependencies
- **Documentation**: Technical documentation
- **Source Code**: License headers where applicable
- **Distribution**: License files included

### Commercial Use
- **Open Source**: All open source components allow commercial use
- **API Services**: Subject to respective service terms
- **Proprietary**: Some components may have restrictions

### License Compatibility
- **KGAS License**: MIT License
- **Compatibility**: Compatible with all included licenses
- **Attribution**: All attribution requirements are met

---

## License Updates

### Monitoring
- **Regular Review**: Quarterly review of license compliance
- **Version Updates**: Monitor for license changes in updates
- **Compliance Check**: Automated compliance checking

### Updates
- **License Changes**: Document any license changes
- **New Dependencies**: Review licenses for new dependencies
- **Removed Dependencies**: Update documentation when removing

---

**Note**: This document should be updated whenever new dependencies are added or existing ones are updated. Always verify license compatibility before adding new dependencies. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
