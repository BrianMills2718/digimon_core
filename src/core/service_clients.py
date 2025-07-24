import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from .service_protocol import ServiceOperation
from .exceptions import ServiceUnavailableError
import logging

logger = logging.getLogger(__name__)


class AnalyticsServiceClient:
    """Real HTTP client for Analytics Service"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_document(self, document: Dict[str, Any], 
                             analysis_modes: List[str]) -> ServiceOperation:
        """Make real HTTP call to analytics service"""
        if not self.session:
            raise ServiceUnavailableError("AnalyticsService", "Session not initialized")
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/analyze",
                json={
                    "document": document,
                    "modes": analysis_modes
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                duration_ms = float(response.headers.get('X-Duration-Ms', 0))
                
                if response.status == 200:
                    return ServiceOperation(
                        success=True,
                        data=response_data,
                        duration_ms=duration_ms
                    )
                else:
                    error_data = await response.text()
                    return ServiceOperation(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status}: {error_data}",
                        duration_ms=duration_ms
                    )
        except asyncio.TimeoutError:
            raise ServiceUnavailableError("AnalyticsService", "Request timeout")
        except aiohttp.ClientError as e:
            raise ServiceUnavailableError("AnalyticsService", str(e))


class IdentityServiceClient:
    """Real HTTP client for Identity Service"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def resolve_entities(self, document: Dict[str, Any]) -> ServiceOperation:
        """Make real HTTP call to identity service"""
        if not self.session:
            raise ServiceUnavailableError("IdentityService", "Session not initialized")
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/resolve",
                json={"document": document},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                duration_ms = float(response.headers.get('X-Duration-Ms', 0))
                
                if response.status == 200:
                    return ServiceOperation(
                        success=True,
                        data=response_data,
                        duration_ms=duration_ms
                    )
                else:
                    error_data = await response.text()
                    return ServiceOperation(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status}: {error_data}",
                        duration_ms=duration_ms
                    )
        except asyncio.TimeoutError:
            raise ServiceUnavailableError("IdentityService", "Request timeout")
        except aiohttp.ClientError as e:
            raise ServiceUnavailableError("IdentityService", str(e))


class TheoryExtractionServiceClient:
    """Real HTTP client for Theory Extraction Service"""
    
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def extract_theories(self, document: Dict[str, Any], 
                             entities: List[Dict[str, Any]], 
                             analytics: List[Any]) -> ServiceOperation:
        """Make real HTTP call to theory extraction service"""
        if not self.session:
            raise ServiceUnavailableError("TheoryExtractionService", "Session not initialized")
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/extract",
                json={
                    "document": document,
                    "entities": entities,
                    "analytics": [a.data if hasattr(a, 'data') else None for a in analytics if not isinstance(a, Exception)]
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                duration_ms = float(response.headers.get('X-Duration-Ms', 0))
                
                if response.status == 200:
                    return ServiceOperation(
                        success=True,
                        data=response_data,
                        duration_ms=duration_ms
                    )
                else:
                    error_data = await response.text()
                    return ServiceOperation(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status}: {error_data}",
                        duration_ms=duration_ms
                    )
        except asyncio.TimeoutError:
            raise ServiceUnavailableError("TheoryExtractionService", "Request timeout")
        except aiohttp.ClientError as e:
            raise ServiceUnavailableError("TheoryExtractionService", str(e))


class QualityServiceClient:
    """Real HTTP client for Quality Service"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def assess_quality(self, document: Dict[str, Any], 
                           entities: List[Dict[str, Any]], 
                           analytics: List[Any],
                           theories: Optional[Dict[str, Any]] = None) -> ServiceOperation:
        """Make real HTTP call to quality service"""
        if not self.session:
            raise ServiceUnavailableError("QualityService", "Session not initialized")
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/assess",
                json={
                    "document": document,
                    "entities": entities,
                    "analytics": [a.data if hasattr(a, 'data') else None for a in analytics if not isinstance(a, Exception)],
                    "theories": theories
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                duration_ms = float(response.headers.get('X-Duration-Ms', 0))
                
                if response.status == 200:
                    return ServiceOperation(
                        success=True,
                        data=response_data,
                        duration_ms=duration_ms
                    )
                else:
                    error_data = await response.text()
                    return ServiceOperation(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status}: {error_data}",
                        duration_ms=duration_ms
                    )
        except asyncio.TimeoutError:
            raise ServiceUnavailableError("QualityService", "Request timeout")
        except aiohttp.ClientError as e:
            raise ServiceUnavailableError("QualityService", str(e))


class ProvenanceServiceClient:
    """Real HTTP client for Provenance Service"""
    
    def __init__(self, base_url: str = "http://localhost:8005"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def track_operation(self, operation: str, 
                            input_data: Dict[str, Any], 
                            output_data: Dict[str, Any]) -> ServiceOperation:
        """Make real HTTP call to provenance service"""
        if not self.session:
            raise ServiceUnavailableError("ProvenanceService", "Session not initialized")
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/track",
                json={
                    "operation": operation,
                    "input": input_data,
                    "output": output_data
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                duration_ms = float(response.headers.get('X-Duration-Ms', 0))
                
                if response.status == 200:
                    return ServiceOperation(
                        success=True,
                        data=response_data,
                        duration_ms=duration_ms
                    )
                else:
                    error_data = await response.text()
                    return ServiceOperation(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status}: {error_data}",
                        duration_ms=duration_ms
                    )
        except asyncio.TimeoutError:
            raise ServiceUnavailableError("ProvenanceService", "Request timeout")
        except aiohttp.ClientError as e:
            raise ServiceUnavailableError("ProvenanceService", str(e))