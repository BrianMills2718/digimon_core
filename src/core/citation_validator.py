"""
Citation Validator for verifying citation integrity.

Validates citations against their sources and ensures provenance chains
are complete and verifiable.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CitationValidator:
    """
    Validates citations and their provenance chains.
    
    Features:
    - Citation source verification
    - Provenance chain validation
    - Bulk validation support
    - Integrity checking
    """
    
    def __init__(self, provenance_manager):
        """
        Initialize the validator.
        
        Args:
            provenance_manager: ProvenanceManager instance
        """
        self.provenance = provenance_manager
    
    async def validate_citation(self, citation_id: str) -> bool:
        """
        Validate a single citation.
        
        Args:
            citation_id: ID of citation to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Get citation
            citation = self.provenance._citations.get(citation_id)
            if not citation:
                logger.warning(f"Citation not found: {citation_id}")
                return False
            
            # Check source exists
            source_id = citation.get("source_id")
            if not source_id:
                logger.warning(f"Citation {citation_id} has no source_id")
                return False
            
            # Verify source exists
            source = await self.provenance.get_source(source_id)
            derived = self.provenance._derived_content.get(source_id)
            
            if not source and not derived:
                logger.warning(f"Source {source_id} not found for citation {citation_id}")
                return False
            
            # Verify text exists in source
            if source:
                content = source.get("content", "")
            else:
                content = derived.get("output_text", "")
            
            citation_text = citation.get("text", "")
            if citation_text not in content:
                logger.warning(f"Citation text not found in source: {citation_id}")
                return False
            
            # Verify positions if provided
            start_pos = citation.get("start_pos", 0)
            end_pos = citation.get("end_pos", len(content))
            
            if start_pos < 0 or end_pos > len(content) or start_pos >= end_pos:
                logger.warning(f"Invalid positions for citation {citation_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating citation {citation_id}: {e}")
            return False
    
    async def validate_provenance_chain(self, citation_id: str) -> bool:
        """
        Validate the complete provenance chain for a citation.
        
        Args:
            citation_id: ID of citation
            
        Returns:
            True if chain is valid, False otherwise
        """
        try:
            chain = await self.provenance.get_provenance_chain(citation_id)
            
            if not chain:
                logger.warning(f"No provenance chain for citation {citation_id}")
                return False
            
            # Verify each link in the chain
            for i in range(len(chain) - 1):
                current = chain[i]
                next_item = chain[i + 1]
                
                # Verify linkage
                if next_item.get("type") == "derived":
                    if next_item.get("source_id") != current.get("id"):
                        logger.warning(f"Broken chain link at position {i}")
                        return False
                elif next_item.get("type") == "citation":
                    # Last item should be the citation
                    if i != len(chain) - 2:
                        logger.warning(f"Citation not at end of chain")
                        return False
            
            # Verify source integrity if it's an original source
            if chain[0].get("type") == "source":
                source_id = chain[0].get("id")
                if not await self.provenance.verify_source_integrity(source_id):
                    logger.warning(f"Source integrity check failed: {source_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating provenance chain for {citation_id}: {e}")
            return False
    
    async def validate_bulk(self, citation_ids: List[str]) -> Dict[str, Any]:
        """
        Validate multiple citations.
        
        Args:
            citation_ids: List of citation IDs to validate
            
        Returns:
            Validation results dictionary
        """
        results = {
            "total": len(citation_ids),
            "valid": 0,
            "invalid": 0,
            "invalid_citations": [],
            "errors": []
        }
        
        for citation_id in citation_ids:
            try:
                if await self.validate_citation(citation_id):
                    results["valid"] += 1
                else:
                    results["invalid"] += 1
                    results["invalid_citations"].append(citation_id)
            except Exception as e:
                results["invalid"] += 1
                results["invalid_citations"].append(citation_id)
                results["errors"].append({
                    "citation_id": citation_id,
                    "error": str(e)
                })
        
        return results
    
    async def find_orphaned_citations(self) -> List[Dict[str, Any]]:
        """
        Find citations with missing or invalid sources.
        
        Returns:
            List of orphaned citation records
        """
        orphaned = []
        
        for citation_id, citation in self.provenance._citations.items():
            source_id = citation.get("source_id")
            
            # Check if source exists
            source_exists = (
                source_id in self.provenance._sources or
                source_id in self.provenance._derived_content
            )
            
            if not source_exists:
                orphaned.append({
                    "citation_id": citation_id,
                    "source_id": source_id,
                    "text": citation.get("text", ""),
                    "created_at": citation.get("created_at", ""),
                    "reason": "source_missing"
                })
            elif not await self.validate_citation(citation_id):
                orphaned.append({
                    "citation_id": citation_id,
                    "source_id": source_id,
                    "text": citation.get("text", ""),
                    "created_at": citation.get("created_at", ""),
                    "reason": "validation_failed"
                })
        
        return orphaned
    
    async def generate_validation_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report.
        
        Returns:
            Validation report with statistics and issues
        """
        all_citations = list(self.provenance._citations.keys())
        validation_results = await self.validate_bulk(all_citations)
        
        # Check provenance chains
        chain_valid = 0
        chain_invalid = 0
        
        for citation_id in all_citations:
            if await self.validate_provenance_chain(citation_id):
                chain_valid += 1
            else:
                chain_invalid += 1
        
        # Find orphaned citations
        orphaned = await self.find_orphaned_citations()
        
        # Get statistics
        stats = await self.provenance.get_citation_statistics()
        
        report = {
            "summary": {
                "total_citations": validation_results["total"],
                "valid_citations": validation_results["valid"],
                "invalid_citations": validation_results["invalid"],
                "valid_chains": chain_valid,
                "invalid_chains": chain_invalid,
                "orphaned_citations": len(orphaned)
            },
            "statistics": stats,
            "issues": {
                "invalid_citations": validation_results["invalid_citations"],
                "orphaned_citations": orphaned,
                "validation_errors": validation_results["errors"]
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return report