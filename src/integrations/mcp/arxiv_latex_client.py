"""
ArXiv LaTeX MCP Client

Client for the arxiv-latex-mcp server providing access to:
- LaTeX source code of ArXiv papers
- Mathematical equation extraction
- Paper structure analysis
- Bibliography extraction

Based on: takashiishida/arxiv-latex-mcp
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .http_client import HTTPMCPClient
from .base_client import MCPResponse
from ...core.circuit_breaker import CircuitBreaker
from ...core.api_rate_limiter import APIRateLimiter
import logging

logger = logging.getLogger(__name__)


@dataclass
class ArXivLatexContent:
    """ArXiv paper LaTeX content representation"""
    arxiv_id: str
    title: str
    main_tex: str
    sections: List[Dict[str, str]]
    equations: List[str]
    figures: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    bibliography: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class ArXivEquation:
    """Mathematical equation from ArXiv paper"""
    equation_id: str
    latex_code: str
    context: str
    section: str
    equation_type: str  # inline, display, align, etc.


class ArXivLatexMCPClient(HTTPMCPClient):
    """
    MCP client for ArXiv LaTeX source access.
    
    Provides access to:
    - Raw LaTeX source of ArXiv papers
    - Structured extraction of mathematical content
    - Paper structure and sections
    - Bibliography and citations in LaTeX format
    """
    
    def __init__(self,
                 rate_limiter: APIRateLimiter,
                 circuit_breaker: CircuitBreaker,
                 server_url: str = "http://localhost:8001"):
        """
        Initialize ArXiv LaTeX MCP client.
        
        Args:
            rate_limiter: Rate limiter instance
            circuit_breaker: Circuit breaker instance
            server_url: MCP server URL
        """
        super().__init__(
            server_name="arxiv_latex",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    async def get_latex_source(self, arxiv_id: str) -> MCPResponse[ArXivLatexContent]:
        """
        Get the complete LaTeX source of an ArXiv paper.
        
        Args:
            arxiv_id: ArXiv paper ID (e.g., "2301.00001" or "math.GT/0309001")
            
        Returns:
            MCPResponse containing LaTeX content
        """
        params = {"arxiv_id": arxiv_id}
        
        response = await self.call_method("get_latex_source", params)
        
        if response.success and response.data:
            content = self._parse_latex_content(response.data)
            return MCPResponse(success=True, data=content, metadata=response.metadata)
        
        return response
    
    async def extract_equations(self, arxiv_id: str,
                              include_context: bool = True) -> MCPResponse[List[ArXivEquation]]:
        """
        Extract all mathematical equations from an ArXiv paper.
        
        Args:
            arxiv_id: ArXiv paper ID
            include_context: Include surrounding text context
            
        Returns:
            MCPResponse containing list of equations
        """
        params = {
            "arxiv_id": arxiv_id,
            "include_context": include_context
        }
        
        response = await self.call_method("extract_equations", params)
        
        if response.success and response.data:
            equations = [self._parse_equation(eq) for eq in response.data.get("equations", [])]
            return MCPResponse(success=True, data=equations, metadata=response.metadata)
        
        return response
    
    async def get_paper_structure(self, arxiv_id: str) -> MCPResponse[Dict[str, Any]]:
        """
        Get the structural outline of an ArXiv paper.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            MCPResponse containing paper structure (sections, subsections, etc.)
        """
        params = {"arxiv_id": arxiv_id}
        
        response = await self.call_method("get_paper_structure", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("structure", {}),
                metadata=response.metadata
            )
        
        return response
    
    async def extract_section(self, arxiv_id: str, 
                            section_name: str) -> MCPResponse[Dict[str, Any]]:
        """
        Extract a specific section from an ArXiv paper.
        
        Args:
            arxiv_id: ArXiv paper ID
            section_name: Name of the section to extract
            
        Returns:
            MCPResponse containing section content
        """
        params = {
            "arxiv_id": arxiv_id,
            "section_name": section_name
        }
        
        response = await self.call_method("extract_section", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("section", {}),
                metadata=response.metadata
            )
        
        return response
    
    async def get_bibliography(self, arxiv_id: str) -> MCPResponse[List[Dict[str, Any]]]:
        """
        Extract bibliography/references from an ArXiv paper.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            MCPResponse containing bibliography entries
        """
        params = {"arxiv_id": arxiv_id}
        
        response = await self.call_method("get_bibliography", params)
        
        if response.success and response.data:
            return MCPResponse(
                success=True,
                data=response.data.get("bibliography", []),
                metadata=response.metadata
            )
        
        return response
    
    async def extract_theorems_proofs(self, arxiv_id: str) -> MCPResponse[List[Dict[str, Any]]]:
        """
        Extract theorems, lemmas, and their proofs from an ArXiv paper.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            MCPResponse containing theorems and proofs
        """
        params = {"arxiv_id": arxiv_id}
        
        response = await self.call_method("extract_theorems_proofs", params)
        
        if response.success and response.data:
            return MCPResponse(
                success=True,
                data=response.data.get("theorems", []),
                metadata=response.metadata
            )
        
        return response
    
    async def extract_figures_tables(self, arxiv_id: str) -> MCPResponse[Dict[str, List[Dict[str, Any]]]]:
        """
        Extract figure and table references/captions from an ArXiv paper.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            MCPResponse containing figures and tables metadata
        """
        params = {"arxiv_id": arxiv_id}
        
        response = await self.call_method("extract_figures_tables", params)
        
        if response.success and response.data:
            return MCPResponse(
                success=True,
                data={
                    "figures": response.data.get("figures", []),
                    "tables": response.data.get("tables", [])
                },
                metadata=response.metadata
            )
        
        return response
    
    # Helper Methods
    
    def _parse_latex_content(self, data: Dict[str, Any]) -> ArXivLatexContent:
        """Parse LaTeX content from MCP response"""
        return ArXivLatexContent(
            arxiv_id=data.get("arxiv_id", ""),
            title=data.get("title", ""),
            main_tex=data.get("main_tex", ""),
            sections=data.get("sections", []),
            equations=data.get("equations", []),
            figures=data.get("figures", []),
            tables=data.get("tables", []),
            bibliography=data.get("bibliography", []),
            metadata=data.get("metadata", {})
        )
    
    def _parse_equation(self, data: Dict[str, Any]) -> ArXivEquation:
        """Parse equation data from MCP response"""
        return ArXivEquation(
            equation_id=data.get("equation_id", ""),
            latex_code=data.get("latex_code", ""),
            context=data.get("context", ""),
            section=data.get("section", ""),
            equation_type=data.get("equation_type", "")
        )