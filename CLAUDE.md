# KGAS Phase 8 - Strategic External Integrations Implementation Guide

## 🎯 Mission & Status
**Target**: Strategic external integrations for development acceleration  
**Status**: 0% complete - Phase 8.1 starting  
**Priority**: Academic API integrations, Infrastructure services, Document processing MCPs

## ⚡ Quick Commands
```bash
# Essential commands for this phase
pytest tests/integration/test_external_apis.py    # Test external integrations
python scripts/validate_api_connections.py       # Validate API connectivity
python -m pip install -r requirements-phase8.txt # Install new dependencies
python scripts/health_check_external_services.py # Check external service health
```

## 💡 Core Principles
1. **Production-Ready Only**: Real API integrations, no mocks for external services
2. **Fail Fast**: Circuit breakers and explicit timeouts for all external calls
3. **Evidence-Based**: All integration claims proven via real API tests
4. **Resilient Architecture**: Graceful degradation when external services unavailable

## 📋 Implementation Checklist
- [ ] **Academic API Integration** - ArXiv, PubMed, Semantic Scholar `src/integrations/academic_apis/`
- [ ] **Document Processing MCPs** - MarkItDown, content extractors `src/integrations/document_mcps/`  
- [ ] **Infrastructure Services** - Monitoring, auth, deployment tools `src/integrations/infrastructure/`
- [ ] **Circuit Breakers** - Resilient external service patterns `src/core/circuit_breaker.py`
- [ ] **API Rate Limiting** - Respectful API usage patterns `src/core/api_rate_limiter.py`
- [ ] **Integration Tests** - All external services work together
- [ ] **Evidence Files** - Document with actual API responses and performance metrics
- [ ] **Validation** - External review of integration architecture

## 🏗️ Key Files & Structure
```
src/
├── integrations/
│   ├── academic_apis/              # Academic database integrations
│   │   ├── arxiv_client.py        # ArXiv API integration
│   │   ├── pubmed_client.py       # PubMed/NCBI integration
│   │   └── semantic_scholar_client.py # Semantic Scholar API
│   ├── document_mcps/              # Document processing integrations
│   │   ├── markitdown_mcp.py      # MarkItDown MCP integration
│   │   └── content_extractor_mcp.py # Multi-format content extraction
│   └── infrastructure/             # Infrastructure service integrations
│       ├── monitoring_client.py    # Observability integrations
│       └── auth_provider.py       # Authentication service integration
├── core/
│   ├── circuit_breaker.py         # Circuit breaker pattern for external services
│   ├── api_rate_limiter.py        # Enhanced rate limiting for external APIs
│   └── external_service_manager.py # Centralized external service management
└── tests/
    ├── integration/test_external_apis.py # Integration tests for all APIs
    └── fixtures/external_api_responses/   # Real API response fixtures
```

## 🔍 Validation Requirements
**Evidence Standard**: Each integration needs Evidence_[Service].md with:
- Real API response samples and performance metrics
- Circuit breaker behavior demonstrations  
- Rate limiting compliance proof
- Fallback/degradation scenarios

**Validation Command**:
```bash
python gemini-review-tool/gemini_review.py --config validation-phase8-integrations.yaml .
```

## ⚠️ Critical Pitfalls
- **No hardcoded API keys** - Use environment variables and secure credential management
- **No unlimited API calls** - Implement proper rate limiting and quotas
- **No single points of failure** - All external dependencies must have fallbacks

---

<details>
<summary>📖 Detailed Implementation Guide (Click to expand)</summary>

### Issue 1: Academic API Integration Framework - HIGH PRIORITY
**File**: `src/integrations/academic_apis/` | **Impact**: Access to 50M+ research papers

**Problem**: Currently limited to local PDF processing, need integration with major academic databases

**Solution**:
1. **ArXiv Integration** - `arxiv_client.py`
   - Real-time paper search and metadata retrieval
   - Full-text PDF download capabilities
   - Citation network analysis from ArXiv references

2. **PubMed Integration** - `pubmed_client.py`
   - NCBI E-utilities API integration for biomedical literature
   - MeSH term extraction and medical concept mapping
   - Author and affiliation network analysis

3. **Semantic Scholar Integration** - `semantic_scholar_client.py`
   - Academic graph API for citation networks
   - Author influence metrics and collaboration patterns
   - Cross-disciplinary research discovery

**Code Example**:
```python
# src/integrations/academic_apis/arxiv_client.py
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ArXivPaper:
    """ArXiv paper metadata with full citation information"""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published: datetime
    pdf_url: str
    citation_count: int
    references: List[str]

class ArXivClient:
    """Production ArXiv API client with rate limiting and error handling"""
    
    def __init__(self, rate_limiter: APIRateLimiter):
        self.base_url = "http://export.arxiv.org/api/query"
        self.rate_limiter = rate_limiter
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def search_papers(self, query: str, max_results: int = 100) -> List[ArXivPaper]:
        """Search ArXiv with real API calls and structured parsing"""
        await self.rate_limiter.acquire("arxiv")  # Respect API limits
        
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            if response.status != 200:
                raise ExternalServiceError(f"ArXiv API error: {response.status}")
                
            xml_content = await response.text()
            papers = self._parse_arxiv_response(xml_content)
            
        # Enrich with citation data from Semantic Scholar
        for paper in papers:
            paper.citation_count = await self._get_citation_count(paper.arxiv_id)
            
        return papers
    
    async def download_pdf(self, arxiv_id: str) -> bytes:
        """Download full-text PDF from ArXiv"""
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        async with self.session.get(pdf_url) as response:
            if response.status != 200:
                raise ExternalServiceError(f"PDF download failed: {response.status}")
            return await response.read()
```

### Issue 2: Document Processing MCP Integration - HIGH PRIORITY
**File**: `src/integrations/document_mcps/` | **Impact**: Support for 20+ document formats

**Problem**: Currently limited to PDF and basic text formats

**Solution**:
1. **MarkItDown MCP Integration** - `markitdown_mcp.py`
   - Microsoft's MarkItDown for Office documents, presentations
   - Real-time conversion to structured markdown
   - Preserve document formatting and metadata

2. **Content Extractor MCP** - `content_extractor_mcp.py`
   - Multi-format content extraction (DOCX, PPTX, XLSX, etc.)
   - OCR integration for scanned documents
   - Structured data extraction from spreadsheets

**Code Example**:
```python
# src/integrations/document_mcps/markitdown_mcp.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from typing import Dict, Any, List
from pathlib import Path

class MarkItDownMCPClient:
    """Production MCP client for MarkItDown document conversion"""
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.session: Optional[ClientSession] = None
        
    async def connect(self):
        """Establish MCP connection with error handling"""
        server_params = StdioServerParameters(
            command="npx",
            args=["@microsoft/markitdown-mcp"]
        )
        
        async with self.circuit_breaker.call("markitdown_mcp"):
            self.session = await ClientSession(server_params).__aenter__()
            
    async def convert_document(self, file_path: Path) -> Dict[str, Any]:
        """Convert document to structured markdown with metadata"""
        if not self.session:
            await self.connect()
            
        # Real MCP call to MarkItDown service
        result = await self.session.call_tool(
            "convert_document",
            arguments={"file_path": str(file_path)}
        )
        
        return {
            "markdown_content": result.content[0].text,
            "metadata": result.metadata,
            "word_count": len(result.content[0].text.split()),
            "conversion_time": result.processing_time
        }
        
    async def batch_convert(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Batch convert multiple documents efficiently"""
        # Use anyio structured concurrency for parallel processing
        import anyio
        
        async def convert_single(path: Path) -> Dict[str, Any]:
            try:
                return await self.convert_document(path)
            except Exception as e:
                return {"error": str(e), "file_path": str(path)}
                
        async with anyio.create_task_group() as tg:
            results = []
            for path in file_paths:
                result = await tg.start_soon(convert_single, path)
                results.append(result)
                
        return results
```

### Issue 3: Infrastructure Service Integration - MEDIUM PRIORITY
**File**: `src/integrations/infrastructure/` | **Impact**: Production deployment readiness

**Problem**: No production monitoring, authentication, or deployment automation

**Solution**:
1. **Monitoring Integration** - `monitoring_client.py`
   - Prometheus metrics collection
   - OpenTelemetry distributed tracing
   - Real-time alerting for service health

2. **Authentication Provider** - `auth_provider.py`
   - OAuth 2.0 integration for academic institutions
   - API key management and rotation
   - Role-based access control

**Code Example**:
```python
# src/integrations/infrastructure/monitoring_client.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

class ProductionMonitoring:
    """Production monitoring with Prometheus and OpenTelemetry"""
    
    def __init__(self):
        # Prometheus metrics
        self.api_requests = Counter('kgas_api_requests_total', 'Total API requests', ['method', 'endpoint'])
        self.processing_time = Histogram('kgas_processing_seconds', 'Time spent processing requests')
        self.active_connections = Gauge('kgas_active_connections', 'Number of active connections')
        
        # OpenTelemetry tracing
        trace.set_tracer_provider(TracerProvider())
        otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:14250")
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        self.tracer = trace.get_tracer(__name__)
        
    async def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics server"""
        start_http_server(port)
        
    def track_api_request(self, method: str, endpoint: str):
        """Track API request metrics"""
        self.api_requests.labels(method=method, endpoint=endpoint).inc()
        
    def track_processing_time(self, duration: float):
        """Track request processing time"""
        self.processing_time.observe(duration)
        
    async def trace_operation(self, operation_name: str, **attributes):
        """Create distributed trace span"""
        with self.tracer.start_as_current_span(operation_name) as span:
            for key, value in attributes.items():
                span.set_attribute(key, value)
            yield span
```

</details>

---

<details>
<summary>🛠️ Environment & Commands (Click to expand)</summary>

### Development Environment
```bash
# Setup Phase 8 dependencies
pip install aiohttp[speedups] httpx[http2] 
pip install prometheus-client opentelemetry-api opentelemetry-sdk
pip install mcp asyncio-throttle circuit-breaker-pattern

# Development workflow  
python scripts/setup_phase8_environment.py
python -m pytest tests/integration/test_external_apis.py -v
python scripts/lint_integration_code.py
```

### Testing Strategy
- **Unit Tests**: `pytest tests/unit/test_integrations/ -v`
- **Integration Tests**: `pytest tests/integration/test_external_apis.py -v` 
- **Performance Tests**: `python scripts/benchmark_external_apis.py`
- **Coverage**: Target 95% minimum for integration code

### Service Dependencies
- ArXiv API → Circuit Breaker → Rate Limiter
- PubMed API → Circuit Breaker → Rate Limiter
- MarkItDown MCP → MCP Client → Error Handler
- All External Services → Monitoring Client

</details>

---

<details>
<summary>🔧 Troubleshooting (Click to expand)</summary>

### Common Issues
**API Rate Limiting**: External service returns 429 Too Many Requests
- **Symptoms**: Requests failing with rate limit errors
- **Cause**: Exceeding API quotas or request frequency limits  
- **Fix**: Implement exponential backoff and respect rate limit headers

**MCP Connection Failures**: Cannot establish MCP server connection
- **Baseline**: MCP server should start within 5 seconds
- **Threshold**: Max 3 connection attempts before fallback
- **Monitor**: Check MCP server logs and process status

### Debug Commands
```bash
python scripts/test_api_connectivity.py     # Test all external API connections
python scripts/check_mcp_servers.py        # Verify MCP server availability  
python scripts/view_integration_logs.py    # View detailed integration logs
```

</details>

## 🚀 **NEXT STEPS AFTER CLAUDE.MD UPDATE**

Based on the roadmap, **Phase 8.1: Core Infrastructure + ADR Implementation** should be the immediate focus:

### **Phase 8.1 Implementation Tasks (Weeks 1-4)**

1. **ADR-007 Uncertainty Metrics Implementation**
   - Implement CERQual framework for academic rigor assessment
   - Create uncertainty propagation through analysis pipelines
   - Add confidence intervals to all analytical results

2. **ADR-006 Cross-Modal Analysis Enhancement** 
   - Build graph ↔ table ↔ vector conversion tools (T91-T100)
   - Implement seamless format switching within analysis workflows
   - Create cross-modal provenance tracking

3. **Core Infrastructure Services**
   - Production monitoring with Prometheus/OpenTelemetry
   - Authentication service with OAuth 2.0 integration
   - Cloud deployment automation (Docker + Kubernetes)

4. **Academic API Integration Foundation**
   - ArXiv API client with rate limiting and circuit breakers
   - PubMed integration for biomedical literature access
   - Semantic Scholar for citation network analysis

The implementation should follow the established TDD methodology with 100% test-first development for all external service integrations.