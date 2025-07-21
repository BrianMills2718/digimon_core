# Task 1.4: Async API Enhancement

**Duration**: Days 6-8 (Week 3)  
**Owner**: Backend Lead  
**Priority**: HIGH - Performance critical for scaling

## Objective

Convert API clients to async operations, implement proper retry logic, add rate limiting, and achieve 50-60% performance improvement in API operations.

## Current State Analysis

### Synchronous API Bottlenecks

```bash
# Analysis script for current API usage
#!/bin/bash

echo "=== API Client Usage Analysis ==="
echo "Synchronous API calls:"
grep -r "requests\." src/ --include="*.py" | grep -v __pycache__ | wc -l

echo "OpenAI client usage:"
grep -r "openai\." src/ --include="*.py" | grep -v __pycache__ | wc -l

echo "Files with blocking API calls:"
grep -r -l "\.post\|\.get\|\.put\|\.delete" src/ --include="*.py" | grep -v __pycache__

echo "Current timeout patterns:"
grep -r "timeout" src/ --include="*.py" | grep -v __pycache__ | head -10
```

### Performance Baseline

```python
# Current performance measurements
CURRENT_PERFORMANCE = {
    'openai_single_call': 2.5,      # seconds average
    'batch_100_entities': 45.0,     # seconds
    'error_recovery': 15.0,         # seconds for retry cycle
    'concurrent_limit': 1,          # effectively synchronous
}

TARGET_PERFORMANCE = {
    'openai_single_call': 1.5,      # 40% improvement
    'batch_100_entities': 20.0,     # 55% improvement  
    'error_recovery': 2.0,          # 85% improvement
    'concurrent_limit': 10,         # 10x concurrency
}
```

## Implementation Plan

### Day 6 Morning: Async Infrastructure

#### Step 1: Create Async API Base Classes
```python
# File: src/core/async_api_clients.py

import asyncio
import aiohttp
import backoff
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum

class APIStatus(Enum):
    SUCCESS = "success"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class APIResponse:
    """Standardized API response wrapper"""
    status: APIStatus
    data: Any = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    retry_count: int = 0

class AsyncAPIClient:
    """Base class for async API clients with rate limiting and retry logic"""
    
    def __init__(self, 
                 base_url: str,
                 api_key: str,
                 rate_limit: int = 60,  # requests per minute
                 max_concurrent: int = 10,
                 timeout: int = 30):
        
        self.base_url = base_url
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        
        # Rate limiting
        self._rate_limiter = asyncio.Semaphore(rate_limit)
        self._concurrent_limiter = asyncio.Semaphore(max_concurrent)
        self._request_times: List[datetime] = []
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._get_default_headers()
            )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Override in subclasses for API-specific headers"""
        return {
            'User-Agent': 'KGAS-AsyncClient/1.0',
            'Content-Type': 'application/json'
        }
    
    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _wait_for_rate_limit(self):
        """Implement rate limiting"""
        now = datetime.now()
        
        # Remove requests older than 1 minute
        cutoff = now - timedelta(minutes=1)
        self._request_times = [t for t in self._request_times if t > cutoff]
        
        # Check if we're at the limit
        if len(self._request_times) >= self.rate_limit:
            sleep_time = 60 - (now - self._request_times[0]).total_seconds()
            if sleep_time > 0:
                self.logger.debug(f"Rate limit reached, sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
        
        self._request_times.append(now)
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def _make_request(self,
                           method: str,
                           endpoint: str,
                           data: Optional[Dict] = None,
                           params: Optional[Dict] = None) -> APIResponse:
        """Make HTTP request with retry logic"""
        
        async with self._concurrent_limiter:
            await self._wait_for_rate_limit()
            await self._ensure_session()
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            start_time = asyncio.get_event_loop().time()
            
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    
                    response_time = asyncio.get_event_loop().time() - start_time
                    response_data = await response.json()
                    
                    if response.status == 429:  # Rate limited
                        return APIResponse(
                            status=APIStatus.RATE_LIMITED,
                            status_code=response.status,
                            response_time=response_time,
                            error="Rate limit exceeded"
                        )
                    
                    if response.status >= 400:
                        return APIResponse(
                            status=APIStatus.ERROR,
                            status_code=response.status,
                            response_time=response_time,
                            error=f"HTTP {response.status}: {response_data}"
                        )
                    
                    return APIResponse(
                        status=APIStatus.SUCCESS,
                        data=response_data,
                        status_code=response.status,
                        response_time=response_time
                    )
                    
            except asyncio.TimeoutError:
                return APIResponse(
                    status=APIStatus.TIMEOUT,
                    response_time=self.timeout,
                    error="Request timeout"
                )
            except Exception as e:
                return APIResponse(
                    status=APIStatus.ERROR,
                    error=str(e),
                    response_time=asyncio.get_event_loop().time() - start_time
                )
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        """Async GET request"""
        return await self._make_request('GET', endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> APIResponse:
        """Async POST request"""
        return await self._make_request('POST', endpoint, data=data)
    
    async def batch_requests(self, requests: List[Dict[str, Any]]) -> List[APIResponse]:
        """Execute multiple requests concurrently"""
        tasks = []
        
        for req in requests:
            method = req.get('method', 'GET')
            endpoint = req['endpoint']
            data = req.get('data')
            params = req.get('params')
            
            task = self._make_request(method, endpoint, data, params)
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        processed_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                processed_responses.append(APIResponse(
                    status=APIStatus.ERROR,
                    error=str(response)
                ))
            else:
                processed_responses.append(response)
        
        return processed_responses
```

#### Step 2: OpenAI Async Client
```python
# File: src/core/async_openai_client.py

from src.core.async_api_clients import AsyncAPIClient, APIResponse, APIStatus
from typing import List, Dict, Any, Optional, Union
import json

class AsyncOpenAIClient(AsyncAPIClient):
    """Async OpenAI API client with enhanced features"""
    
    def __init__(self, api_key: str, organization: Optional[str] = None):
        super().__init__(
            base_url="https://api.openai.com/v1",
            api_key=api_key,
            rate_limit=60,  # Adjust based on your tier
            max_concurrent=5,  # Conservative for OpenAI
            timeout=60
        )
        self.organization = organization
    
    def _get_default_headers(self) -> Dict[str, str]:
        """OpenAI-specific headers"""
        headers = super()._get_default_headers()
        headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        if self.organization:
            headers['OpenAI-Organization'] = self.organization
            
        return headers
    
    async def create_completion(self,
                               model: str = "gpt-4",
                               messages: List[Dict[str, str]] = None,
                               prompt: Optional[str] = None,
                               max_tokens: int = 2000,
                               temperature: float = 0.7,
                               **kwargs) -> APIResponse:
        """Create chat completion"""
        
        if messages is None and prompt:
            messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        return await self.post("chat/completions", data)
    
    async def create_embeddings(self,
                               texts: Union[str, List[str]],
                               model: str = "text-embedding-3-small") -> APIResponse:
        """Create embeddings for text(s)"""
        
        if isinstance(texts, str):
            texts = [texts]
        
        data = {
            "model": model,
            "input": texts
        }
        
        return await self.post("embeddings", data)
    
    async def batch_completions(self,
                               prompts: List[str],
                               model: str = "gpt-4",
                               max_tokens: int = 2000,
                               temperature: float = 0.7) -> List[APIResponse]:
        """Process multiple prompts concurrently"""
        
        requests = []
        for prompt in prompts:
            requests.append({
                'method': 'POST',
                'endpoint': 'chat/completions',
                'data': {
                    'model': model,
                    'messages': [{"role": "user", "content": prompt}],
                    'max_tokens': max_tokens,
                    'temperature': temperature
                }
            })
        
        return await self.batch_requests(requests)
    
    async def batch_embeddings(self,
                              text_batches: List[List[str]],
                              model: str = "text-embedding-3-small") -> List[APIResponse]:
        """Process multiple embedding batches concurrently"""
        
        requests = []
        for batch in text_batches:
            requests.append({
                'method': 'POST',
                'endpoint': 'embeddings',
                'data': {
                    'model': model,
                    'input': batch
                }
            })
        
        return await self.batch_requests(requests)
```

### Day 6 Afternoon: Tool Integration

#### Step 3: Convert LLM-Based Tools
```python
# File: src/tools/phase2/async_ontology_extractor.py

import asyncio
from typing import Dict, Any, Optional, List
from src.core.kgas_tool_interface import KGASTool, ToolMetadata
from src.core.async_openai_client import AsyncOpenAIClient
import json

class AsyncOntologyAwareExtractor(KGASTool):
    """Async version of ontology-aware entity extractor"""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            tool_id="T23c_async",
            name="Async Ontology-Aware Extractor",
            description="Extract entities using LLM with domain ontology (async)",
            category="extraction",
            tags=["llm", "ontology", "async", "entities"]
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with async OpenAI client"""
        self.config = config or {}
        
        api_key = self.config.get('openai_api_key')
        if not api_key:
            raise ValueError("OpenAI API key required")
            
        self.client = AsyncOpenAIClient(
            api_key=api_key,
            organization=self.config.get('openai_organization')
        )
        
        self.model = self.config.get('model', 'gpt-4')
        self.max_tokens = self.config.get('max_tokens', 2000)
        self.temperature = self.config.get('temperature', 0.3)
    
    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute async entity extraction"""
        try:
            self.ensure_initialized()
            
            # Handle validation mode
            if context and context.get('validation_mode'):
                return self.create_result(
                    status='success',
                    results={'entities': [], 'validation': True}
                )
            
            # Extract required data
            text = input_data.get('text', '')
            ontology = input_data.get('ontology', {})
            
            if not text:
                return self.create_result(
                    status='error',
                    error='Text is required for extraction'
                )
            
            # Process in chunks for large texts
            chunks = self._chunk_text(text, max_length=3000)
            
            # Process all chunks concurrently
            async with self.client:
                start_time = asyncio.get_event_loop().time()
                
                # Create prompts for all chunks
                prompts = [
                    self._create_extraction_prompt(chunk, ontology)
                    for chunk in chunks
                ]
                
                # Execute all extractions concurrently
                responses = await self.client.batch_completions(
                    prompts=prompts,
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                execution_time = asyncio.get_event_loop().time() - start_time
                
                # Process responses
                all_entities = []
                for i, response in enumerate(responses):
                    if response.status == APIStatus.SUCCESS:
                        chunk_entities = self._parse_extraction_response(
                            response.data, chunks[i]
                        )
                        all_entities.extend(chunk_entities)
                
                # Deduplicate entities
                unique_entities = self._deduplicate_entities(all_entities)
                
                return self.create_result(
                    status='success',
                    results={
                        'entities': unique_entities,
                        'total_entities': len(unique_entities),
                        'chunks_processed': len(chunks),
                        'concurrent_requests': len(prompts)
                    },
                    execution_time=execution_time
                )
                
        except Exception as e:
            return self.create_result(
                status='error',
                error=f'Async extraction failed: {str(e)}'
            )
    
    def _chunk_text(self, text: str, max_length: int = 3000) -> List[str]:
        """Split text into chunks for processing"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _create_extraction_prompt(self, text: str, ontology: Dict[str, Any]) -> str:
        """Create extraction prompt for text chunk"""
        
        entity_types = list(ontology.get('entities', {}).keys())
        
        prompt = f"""
Extract entities from the following text using the provided ontology.

ONTOLOGY:
Entity Types: {', '.join(entity_types)}
{json.dumps(ontology, indent=2)}

TEXT:
{text}

Return entities as JSON array with format:
[
  {{
    "text": "entity text",
    "type": "entity_type",
    "confidence": 0.95,
    "start": 0,
    "end": 10,
    "properties": {{}}
  }}
]

Only extract entities that match the ontology. Ensure high confidence (>0.7).
"""
        return prompt
    
    def _parse_extraction_response(self, response_data: Dict[str, Any], source_text: str) -> List[Dict[str, Any]]:
        """Parse LLM response into entities"""
        try:
            content = response_data['choices'][0]['message']['content']
            
            # Extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                return []
            
            json_str = content[start_idx:end_idx]
            entities = json.loads(json_str)
            
            # Add source information
            for entity in entities:
                entity['source_text'] = source_text
                entity['extraction_method'] = 'llm_async'
            
            return entities
            
        except (json.JSONDecodeError, KeyError, IndexError):
            return []
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.get('text', '').lower(), entity.get('type', ''))
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capabilities"""
        return {
            'async': True,
            'batch': True,
            'streaming': False,
            'requires_auth': True,
            'concurrent_processing': True
        }
```

## Performance Testing Framework

```python
# File: tests/performance/test_async_performance.py

import pytest
import asyncio
import time
from src.tools.phase2.async_ontology_extractor import AsyncOntologyAwareExtractor

class TestAsyncPerformance:
    """Performance tests for async implementations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_vs_sequential_processing(self):
        """Compare concurrent vs sequential processing times"""
        
        # Setup
        extractor = AsyncOntologyAwareExtractor()
        extractor.initialize({'openai_api_key': 'test-key'})
        
        test_texts = [f"Test document {i} with content." for i in range(10)]
        test_ontology = {'entities': {'Concept': {'properties': ['name']}}}
        
        # Sequential processing
        start_time = time.time()
        sequential_results = []
        for text in test_texts:
            result = await extractor.execute({
                'text': text,
                'ontology': test_ontology
            })
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Concurrent processing
        start_time = time.time()
        tasks = [
            extractor.execute({
                'text': text,
                'ontology': test_ontology
            })
            for text in test_texts
        ]
        concurrent_results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        # Verify improvement
        improvement = (sequential_time - concurrent_time) / sequential_time * 100
        
        print(f"Sequential: {sequential_time:.2f}s")
        print(f"Concurrent: {concurrent_time:.2f}s")  
        print(f"Improvement: {improvement:.1f}%")
        
        assert improvement > 40, f"Expected >40% improvement, got {improvement:.1f}%"
        assert len(concurrent_results) == len(sequential_results)
    
    @pytest.mark.asyncio 
    async def test_rate_limiting_behavior(self):
        """Test rate limiting doesn't break under load"""
        
        # Create client with low rate limit for testing
        from src.core.async_openai_client import AsyncOpenAIClient
        
        client = AsyncOpenAIClient(
            api_key='test-key',
            rate_limit=5  # 5 requests per minute for testing
        )
        
        # Send 10 requests rapidly
        start_time = time.time()
        tasks = [
            client.create_completion(prompt=f"Test prompt {i}")
            for i in range(10)
        ]
        
        responses = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Should take at least 1 minute due to rate limiting
        assert total_time >= 60, f"Rate limiting failed: {total_time:.2f}s"
        
        # All requests should eventually succeed or be rate limited
        statuses = [r.status for r in responses]
        assert all(s in ['success', 'rate_limited'] for s in statuses)
```

## Success Criteria

- [ ] 50-60% performance improvement in API operations
- [ ] Proper async/await implementation throughout
- [ ] Rate limiting prevents API quota issues  
- [ ] Retry logic handles transient failures
- [ ] Concurrent processing works reliably
- [ ] All async tools maintain compatibility

## Deliverables

1. **Async API client framework**
2. **Converted LLM-based tools** (3 tools)
3. **Performance test suite**
4. **Migration guide for remaining tools**
5. **Configuration updates for async settings**