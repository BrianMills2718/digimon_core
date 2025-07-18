"""
Real Performance Testing Framework

Tests actual performance improvements with real document processing.
"""

import asyncio
import unittest
import time
import tempfile
import json
from pathlib import Path
from typing import List

from src.tools.phase2.async_multi_document_processor import AsyncMultiDocumentProcessor, DocumentInput
from src.core.config import ConfigurationManager

class RealPerformanceTest(unittest.TestCase):
    """Test real performance improvements with actual document processing."""
    
    def setUp(self):
        """Set up test environment with real documents."""
        self.config = ConfigurationManager()
        self.processor = AsyncMultiDocumentProcessor(self.config)
        
        # Create test documents with real content
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_documents = self._create_test_documents()
    
    def _create_test_documents(self) -> List[DocumentInput]:
        """Create real test documents for performance testing."""
        
        documents = []
        
        # Create text documents with substantial content
        for i in range(10):
            doc_path = self.test_dir / f"document_{i}.txt"
            content = self._generate_realistic_content(1000)  # 1000 words
            
            with open(doc_path, 'w') as f:
                f.write(content)
            
            documents.append(DocumentInput(
                document_id=f"doc_{i}",
                path=str(doc_path),
                query="Extract all entities and relationships"
            ))
        
        return documents
    
    def _generate_realistic_content(self, word_count: int) -> str:
        """Generate realistic document content for testing."""
        
        entities = [
            "John Smith", "Mary Johnson", "Acme Corporation", "New York",
            "artificial intelligence", "machine learning", "data processing",
            "Q1 2024", "revenue growth", "market analysis"
        ]
        
        content_parts = []
        for i in range(word_count // 20):
            sentence_entities = entities[i % len(entities)]
            sentence = f"This document discusses {sentence_entities} and its impact on business operations. "
            content_parts.append(sentence)
        
        return ' '.join(content_parts)
    
    def test_real_parallel_vs_sequential_performance(self):
        """Test actual parallel vs sequential performance with real documents."""
        
        async def run_test():
            await self.processor.initialize()
            
            # Sequential processing baseline
            sequential_start = time.time()
            sequential_results = []
            
            for document in self.test_documents:
                result = await self.processor._process_single_document_sequential(document)
                sequential_results.append(result)
            
            sequential_time = time.time() - sequential_start
            
            # Parallel processing
            parallel_start = time.time()
            parallel_results = await self.processor.process_documents_async([d.path for d in self.test_documents], [d.query for d in self.test_documents])
            parallel_time = time.time() - parallel_start
            
            # Calculate improvement
            improvement_percent = ((sequential_time - parallel_time) / sequential_time) * 100
            
            # Log results to Evidence.md
            evidence = {
                'test': 'real_parallel_vs_sequential_performance',
                'timestamp': time.time(),
                'documents_processed': len(self.test_documents),
                'sequential_time': sequential_time,
                'parallel_time': parallel_time,
                'improvement_percent': improvement_percent,
                'sequential_success_count': len([r for r in sequential_results if r.success]),
                'parallel_success_count': parallel_results.get("successful_documents", 0)
            }
            
            self._log_evidence(evidence)
            
            # Assertions
            self.assertGreater(improvement_percent, 0, "Parallel processing should be faster than sequential")
            self.assertGreater(improvement_percent, 20, "Performance improvement should be at least 20%")
            
            await self.processor.close()
            
            return evidence
        
        return asyncio.run(run_test())
    
    def _log_evidence(self, evidence: dict):
        """Log performance evidence to Evidence.md file."""
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        
        with open('Evidence.md', 'a') as f:
            f.write(f"\n## Real Performance Test Evidence\n")
            f.write(f"**Timestamp**: {timestamp}\n")
            f.write(f"**Test**: {evidence['test']}\n")
            f.write(f"**Documents Processed**: {evidence['documents_processed']}\n")
            f.write(f"**Sequential Time**: {evidence['sequential_time']:.3f} seconds\n")
            f.write(f"**Parallel Time**: {evidence['parallel_time']:.3f} seconds\n")
            f.write(f"**Performance Improvement**: {evidence['improvement_percent']:.1f}%\n")
            f.write(f"**Success Rates**: {evidence['parallel_success_count']}/{evidence['documents_processed']}\n")
            f.write(f"```json\n{json.dumps(evidence, indent=2)}\n```\n\n")

if __name__ == '__main__':
    unittest.main()