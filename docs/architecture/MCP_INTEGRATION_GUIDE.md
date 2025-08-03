# MCP Integration Guide

This guide explains how to use the Model Context Protocol (MCP) integration in the KGAS system for comprehensive discourse analysis.

## Overview

The MCP integration provides unified access to multiple data sources through standardized MCP servers:

- **Semantic Scholar** - Academic papers, citations, author profiles
- **ArXiv LaTeX** - Mathematical content, equations, theorems
- **YouTube** - Video transcripts with high-quality Whisper transcription
- **Google News** - Real-time news with categorization and trends
- **DappierAI** - Multi-domain trusted media sources
- **Content Core** - Multi-format content extraction

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MCP Orchestrator                       │
├─────────────────────────────────────────────────────────┤
│  - Unified Search Interface                             │
│  - Cross-Source Correlation                             │
│  - Intelligent Routing                                  │
│  - Result Aggregation                                   │
└─────────────┬───────────────────────────────────────────┘
              │
     ┌────────┴────────┬────────┬────────┬────────┬────────┐
     │                 │        │        │        │        │
┌────▼─────┐ ┌────────▼──┐ ┌───▼────┐ ┌─▼──────┐ ┌▼───────┐
│Semantic  │ │ArXiv      │ │YouTube │ │Google  │ │Dappier │
│Scholar   │ │LaTeX      │ │        │ │News    │ │AI      │
│MCP Client│ │MCP Client │ │MCP     │ │MCP     │ │MCP     │
└──────────┘ └───────────┘ └────────┘ └────────┘ └────────┘
```

## Setup

### 1. Install MCP Servers

Each MCP server needs to be installed separately:

```bash
# Semantic Scholar
git clone https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server
cd semantic-scholar-fastmcp-mcp-server
pip install -r requirements.txt

# ArXiv LaTeX
pip install arxiv-latex-mcp

# YouTube
pip install youtube-mcp

# Google News (requires SerpAPI key)
pip install google-news-mcp-server

# DappierAI
pip install dappier-mcp

# Content Core
pip install content-core-mcp
```

### 2. Configure MCP Servers

Create a configuration file:

```python
MCP_CONFIG = {
    # Enable/disable specific servers
    'enable_semantic_scholar': True,
    'enable_arxiv_latex': True,
    'enable_youtube': True,
    'enable_google_news': True,
    'enable_dappier': True,
    'enable_content_core': True,
    
    # API Keys (optional for some services)
    'semantic_scholar_api_key': 'your_key_here',  # Optional, higher rate limits
    'openai_api_key': 'your_openai_key',  # For YouTube Whisper transcription
    'serp_api_key': 'your_serp_key',  # Required for Google News
    'dappier_api_key': 'your_dappier_key',  # Required for DappierAI
    
    # Server URLs (if not using default ports)
    'semantic_scholar_url': 'http://localhost:8000',
    'arxiv_latex_url': 'http://localhost:8001',
    'youtube_url': 'http://localhost:8002',
    'google_news_url': 'http://localhost:8003',
    'dappier_url': 'http://localhost:8004',
    'content_core_url': 'http://localhost:8005'
}
```

### 3. Start MCP Servers

Each server needs to be running:

```bash
# Semantic Scholar
python -m semantic_scholar.server --port 8000

# ArXiv LaTeX
arxiv-latex-mcp serve --port 8001

# YouTube
youtube-mcp serve --port 8002

# Google News
google-news-mcp serve --port 8003 --api-key YOUR_SERP_KEY

# DappierAI
dappier-mcp serve --port 8004 --api-key YOUR_DAPPIER_KEY

# Content Core
content-core-mcp serve --port 8005
```

## Usage Examples

### Basic Setup

```python
from src.integrations.mcp import MCPOrchestrator

# Initialize orchestrator
orchestrator = MCPOrchestrator(MCP_CONFIG)
```

### Unified Search

Search across all configured sources:

```python
from src.integrations.mcp.orchestrator import SearchScope

# Search all sources
results = await orchestrator.unified_search(
    query="artificial intelligence ethics",
    scope=SearchScope.ALL,
    limit_per_source=20
)

# Search only academic sources
academic_results = await orchestrator.unified_search(
    query="deep learning transformers",
    scope=SearchScope.ACADEMIC,
    limit_per_source=50
)

# Search only news sources
news_results = await orchestrator.unified_search(
    query="AI regulation",
    scope=SearchScope.NEWS,
    date_from=datetime.now() - timedelta(days=7),
    date_to=datetime.now()
)

# Process results
for result in results:
    print(f"Source: {result.source}")
    print(f"Title: {result.title}")
    print(f"Summary: {result.summary}")
    print(f"Relevance: {result.relevance_score}")
    print("---")
```

### Discourse Analysis

Analyze discourse across multiple sources:

```python
# Comprehensive discourse analysis
analysis = await orchestrator.analyze_discourse(
    topic="climate change",
    time_range_days=30,
    include_sentiment=True
)

print(f"Topic: {analysis.topic}")
print(f"Time Range: {analysis.time_range}")
print(f"Academic Papers: {len(analysis.academic_papers)}")
print(f"News Articles: {len(analysis.news_articles)}")
print(f"Media Content: {len(analysis.media_content)}")
print(f"Trending Score: {analysis.trending_score}")
print(f"Sentiment: {analysis.sentiment_analysis}")

# Key entities
print("\nKey Entities:")
for entity in analysis.key_entities[:10]:
    print(f"  {entity['name']} ({entity['type']}): {entity['count']} mentions")

# Cross-references
print("\nCross-References:")
for ref in analysis.cross_references[:5]:
    print(f"  {ref['type']}: {ref['source'].title} → {ref['target'].title}")
```

### Mathematical Content Extraction

Extract LaTeX and equations from ArXiv papers:

```python
# Extract mathematical content
math_content = await orchestrator.extract_mathematical_content('2301.00001')

# LaTeX source
print(f"Title: {math_content['latex_content'].title}")
print(f"Main TeX: {math_content['latex_content'].main_tex[:500]}...")

# Equations
print("\nEquations:")
for eq in math_content['equations']:
    print(f"  {eq.latex_code}")
    print(f"  Context: {eq.context}")
    print(f"  Section: {eq.section}")

# Theorems
print("\nTheorems:")
for theorem in math_content['theorems']:
    print(f"  {theorem['type']}: {theorem['statement']}")
```

### Video Transcription and Analysis

Transcribe and analyze YouTube videos:

```python
# Transcribe video
video_analysis = await orchestrator.transcribe_and_analyze_video(
    video_url="https://youtube.com/watch?v=VIDEO_ID",
    extract_topics=True
)

video = video_analysis['video']
print(f"Title: {video.title}")
print(f"Duration: {video.duration} seconds")
print(f"Language: {video.language}")
print(f"Total Words: {video.total_words}")

# Transcript chunks
print("\nTranscript:")
for chunk in video.transcript_chunks[:5]:
    print(f"[{chunk.start_time}-{chunk.end_time}] {chunk.text}")

# Summary
if video_analysis['summary']:
    print(f"\nSummary: {video_analysis['summary']['summary']}")

# Topic timestamps
if 'topic_timestamps' in video_analysis:
    print("\nTopic Timestamps:")
    for topic in video_analysis['topic_timestamps']:
        print(f"  {topic['topic']} at {topic['timestamp']}")
```

### Comprehensive News Coverage

Get news from multiple sources:

```python
# Get comprehensive news coverage
news_coverage = await orchestrator.get_comprehensive_news_coverage(
    topic="artificial intelligence",
    include_financial=True
)

# Google News
if 'google_news' in news_coverage:
    gn = news_coverage['google_news']
    print("Google News Headlines:")
    for article in gn['headlines']:
        print(f"  - {article.title} ({article.source})")
    
    print("\nTrending Topics:")
    for topic in gn['trending']:
        print(f"  - {topic.topic_name} (score: {topic.trending_score})")

# DappierAI Multi-domain
if 'dappier' in news_coverage:
    dappier = news_coverage['dappier']
    print("\nDappier Content:")
    for content in dappier['content']:
        print(f"  - {content.title}")
        print(f"    Source: {content.source} (reputation: {content.source_reputation})")
        print(f"    Domain: {content.domain.value}")
    
    # Financial data if available
    if 'financial' in dappier:
        print("\nFinancial Data:")
        for stock in dappier['financial']:
            print(f"  {stock.symbol}: ${stock.price} ({stock.change_percent}%)")
```

### Direct Client Access

For specific operations, access MCP clients directly:

```python
# Semantic Scholar specific operations
async with orchestrator.clients['semantic_scholar'].connect() as client:
    # Get author details
    author = await client.get_author_details("1741101")
    print(f"Author: {author.data.name}")
    print(f"H-Index: {author.data.h_index}")
    print(f"Papers: {author.data.paper_count}")
    
    # Get paper recommendations
    recommendations = await client.get_recommendations_multi(
        positive_paper_ids=["649def34f8be52c8b66281af98ae884c09aef38b"],
        negative_paper_ids=["ArXiv:1805.02262"],
        limit=10
    )

# Content extraction
async with orchestrator.clients['content_core'].connect() as client:
    # Extract from any URL
    content = await client.extract_content(
        url="https://example.com/document.pdf",
        extract_tables=True,
        extract_images=True
    )
    
    print(f"Content Type: {content.data.content_type}")
    print(f"Word Count: {content.data.word_count}")
    print(f"Tables Found: {len(content.data.structured_data.get('tables', []))}")
```

## Best Practices

### 1. Rate Limiting

The system automatically handles rate limiting, but be mindful of limits:

```python
# Check rate limit status
stats = orchestrator.rate_limiter.get_all_stats()
for service, stat in stats.items():
    print(f"{service}: {stat['requests_made']} requests")
    print(f"  Available tokens: {stat['tokens_available']}")
```

### 2. Error Handling

Always handle potential errors:

```python
try:
    results = await orchestrator.unified_search("query")
except ServiceUnavailableError as e:
    print(f"Service {e.service_name} is unavailable: {e}")
except MCPError as e:
    print(f"MCP error: {e}")
```

### 3. Circuit Breaker Status

Monitor circuit breaker status:

```python
# Get circuit breaker status
for service_name, client in orchestrator.clients.items():
    health = client.get_health_status()
    print(f"{service_name}: {health['circuit_breaker_state']}")
```

### 4. Batch Operations

Use batch operations when possible:

```python
# Batch paper retrieval
async with orchestrator.clients['semantic_scholar'].connect() as client:
    papers = await client.get_papers_batch(
        paper_ids=["id1", "id2", "id3", ...],
        fields="title,abstract,authors,year"
    )
```

## Advanced Usage

### Custom Search Ranking

Implement custom ranking for unified search results:

```python
def custom_ranker(results: List[UnifiedSearchResult]) -> List[UnifiedSearchResult]:
    # Prioritize recent academic papers
    def score(result):
        base_score = result.relevance_score
        
        # Boost academic sources
        if result.source == "semantic_scholar":
            base_score *= 1.5
        
        # Boost recent content
        if result.published_date:
            days_old = (datetime.now() - result.published_date).days
            if days_old < 30:
                base_score *= 1.2
        
        return base_score
    
    return sorted(results, key=score, reverse=True)

# Use custom ranker
results = await orchestrator.unified_search("AI safety")
ranked_results = custom_ranker(results)
```

### Parallel Processing

Process multiple queries in parallel:

```python
async def analyze_multiple_topics(topics: List[str]):
    tasks = []
    for topic in topics:
        task = orchestrator.analyze_discourse(topic, time_range_days=7)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    analyses = {}
    for topic, result in zip(topics, results):
        if isinstance(result, Exception):
            print(f"Error analyzing {topic}: {result}")
        else:
            analyses[topic] = result
    
    return analyses

# Analyze multiple topics
topics = ["AI ethics", "climate change", "quantum computing"]
analyses = await analyze_multiple_topics(topics)
```

### Export Results

Export discourse analysis results:

```python
import json
from datetime import datetime

def export_discourse_analysis(analysis: DiscourseAnalysisResult, filename: str):
    export_data = {
        'topic': analysis.topic,
        'generated_at': datetime.now().isoformat(),
        'time_range': {
            'start': analysis.time_range['start'].isoformat(),
            'end': analysis.time_range['end'].isoformat()
        },
        'statistics': {
            'academic_papers': len(analysis.academic_papers),
            'news_articles': len(analysis.news_articles),
            'media_content': len(analysis.media_content),
            'trending_score': analysis.trending_score
        },
        'sentiment': analysis.sentiment_analysis,
        'key_entities': analysis.key_entities[:20],
        'papers': [
            {
                'title': p.title,
                'authors': [a['name'] for a in p.authors[:3]],
                'year': p.year,
                'citations': p.citation_count
            }
            for p in analysis.academic_papers[:10]
        ],
        'news': [
            {
                'title': a.title,
                'source': getattr(a, 'source', 'Unknown'),
                'date': a.published_date.isoformat() if a.published_date else None
            }
            for a in analysis.news_articles[:10]
        ]
    }
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)

# Export analysis
analysis = await orchestrator.analyze_discourse("AI safety")
export_discourse_analysis(analysis, "ai_safety_discourse.json")
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Responding**
   - Check if the server is running: `curl http://localhost:PORT/health`
   - Verify firewall settings
   - Check server logs

2. **Rate Limit Errors**
   - Check API key configuration
   - Monitor rate limit status
   - Implement exponential backoff

3. **Circuit Breaker Open**
   - Check service health
   - Wait for recovery timeout
   - Manually reset if needed

### Debug Mode

Enable debug logging:

```python
import logging

# Enable debug logging
logging.getLogger('src.integrations.mcp').setLevel(logging.DEBUG)

# See all MCP communication
logging.getLogger('src.integrations.mcp.http_client').setLevel(logging.DEBUG)
```

## Performance Optimization

### Caching

Implement caching for frequently accessed data:

```python
from functools import lru_cache
from typing import Tuple

class CachedMCPOrchestrator(MCPOrchestrator):
    @lru_cache(maxsize=100)
    async def cached_search(self, query: str, scope: str) -> Tuple[UnifiedSearchResult, ...]:
        results = await self.unified_search(query, SearchScope(scope))
        return tuple(results)  # Convert to tuple for hashing
```

### Connection Pooling

The system uses connection pooling by default. Adjust if needed:

```python
# In configuration
MCP_CONFIG['connection_pool_size'] = 100
MCP_CONFIG['connection_timeout'] = 30
```

## Security Considerations

1. **API Key Management**
   - Store API keys in environment variables
   - Never commit keys to version control
   - Rotate keys regularly

2. **Input Validation**
   - Sanitize search queries
   - Validate URLs before extraction
   - Limit batch operation sizes

3. **Network Security**
   - Use HTTPS for MCP servers in production
   - Implement authentication if exposing endpoints
   - Monitor for unusual activity

## Future Enhancements

- Additional MCP servers for social media platforms
- Real-time streaming for live discourse analysis
- Machine learning models for better cross-reference detection
- Visualization tools for discourse analysis results
- Integration with graph databases for relationship mapping