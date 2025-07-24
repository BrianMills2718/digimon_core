#!/usr/bin/env python3
"""
Systematic processor for massive academic texts using our uncertainty methodology
"""

import asyncio
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import sys
import re
from dataclasses import dataclass

# Add uncertainty tools to path
sys.path.append('/home/brian/projects/Digimons/uncertainty_stress_test/core_services')

from formal_bayesian_llm_engine import FormalBayesianLLMEngine

@dataclass
class TextChunk:
    """Structured text chunk for analysis"""
    content: str
    start_pos: int
    end_pos: int
    chunk_id: str
    metadata: Dict[str, Any]

@dataclass
class ExtractedInsight:
    """Key insight extracted from text"""
    content: str
    confidence: float
    source_chunk: str
    methodology: str
    relevance_score: float
    summary: str

class MassiveTextProcessor:
    """
    Processes massive academic texts systematically using uncertainty methodology
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.bayesian_engine = FormalBayesianLLMEngine(self.api_key)
        
        # Processing configuration
        self.chunk_size = 4000  # ~2 pages per chunk
        self.overlap_size = 500  # Overlap to preserve context
        self.min_chunk_size = 1000  # Minimum viable chunk
        
        # Analysis results
        self.processed_chunks = []
        self.extracted_insights = []
        self.processing_metadata = {}
    
    def chunk_text_intelligently(self, text: str, filename: str) -> List[TextChunk]:
        """
        Intelligently chunk massive text while preserving semantic boundaries
        """
        print(f"📄 Chunking {filename} ({len(text):,} chars)...")
        
        # First, try to identify natural boundaries
        section_patterns = [
            r'\n\n[A-Z][A-Z\s]+\n',  # All caps headers
            r'\n\d+\.\s+[A-Z]',       # Numbered sections
            r'\n[A-Z][a-z]+\s[A-Z]',  # Title Case headers
            r'\n\n[A-Z]'              # Paragraph breaks with capitals
        ]
        
        # Find potential break points
        break_points = [0]
        for pattern in section_patterns:
            matches = list(re.finditer(pattern, text))
            break_points.extend([m.start() for m in matches])
        
        break_points = sorted(set(break_points))
        break_points.append(len(text))
        
        chunks = []
        for i in range(len(break_points) - 1):
            start = break_points[i]
            end = min(break_points[i + 1], start + self.chunk_size)
            
            # Extend to next natural break if close
            if end < len(text) and (break_points[i + 1] - end) < self.overlap_size:
                end = break_points[i + 1]
            
            # Skip if too small
            if end - start < self.min_chunk_size:
                continue
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk = TextChunk(
                    content=chunk_text,
                    start_pos=start,
                    end_pos=end,
                    chunk_id=f"{filename}_chunk_{len(chunks)+1:03d}",
                    metadata={
                        "filename": filename,
                        "char_count": len(chunk_text),
                        "word_count": len(chunk_text.split()),
                        "chunk_index": len(chunks) + 1
                    }
                )
                chunks.append(chunk)
        
        print(f"✅ Created {len(chunks)} intelligent chunks")
        return chunks
    
    async def analyze_chunk_for_insights(self, chunk: TextChunk, 
                                       target_domain: str = "uncertainty_methodology") -> List[ExtractedInsight]:
        """
        Extract key insights from a text chunk using Bayesian assessment
        """
        
        # Define claims to test against this chunk
        test_claims = [
            "This text contains novel methodological approaches",
            "This text presents empirical validation methods", 
            "This text discusses uncertainty quantification",
            "This text contains practical implementation guidance",
            "This text presents theoretical frameworks",
        ]
        
        insights = []
        
        for claim in test_claims:
            try:
                # Use formal Bayesian assessment
                assessment = await self.bayesian_engine.assess_claim_with_formal_bayesian(
                    chunk.content, claim, target_domain
                )
                
                # Extract insight if confidence is high enough
                if assessment['posterior_belief'] > 0.6:  # High confidence threshold
                    
                    # Generate insight summary
                    summary = await self._generate_insight_summary(
                        chunk.content, claim, assessment
                    )
                    
                    insight = ExtractedInsight(
                        content=chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content,
                        confidence=assessment['posterior_belief'],
                        source_chunk=chunk.chunk_id,
                        methodology="formal_bayesian_assessment",
                        relevance_score=assessment['bayes_factor'],
                        summary=summary
                    )
                    insights.append(insight)
                    
            except Exception as e:
                print(f"⚠️ Error analyzing chunk {chunk.chunk_id}: {e}")
                continue
        
        return insights
    
    async def _generate_insight_summary(self, text: str, claim: str, 
                                      assessment: Dict) -> str:
        """Generate concise summary of the insight"""
        
        prompt = f"""
        Based on this Bayesian assessment, provide a concise 2-3 sentence summary 
        of the key insight from this text.
        
        CLAIM: {claim}
        CONFIDENCE: {assessment['posterior_belief']:.3f}
        BAYES FACTOR: {assessment['bayes_factor']:.3f}
        
        TEXT EXCERPT: {text[:1000]}...
        
        BAYESIAN REASONING: {assessment['parameters']['parameter_reasoning'].get('bayes_factor_interpretation', 'No reasoning available')}
        
        Provide a summary focusing on:
        1. What specific methodology or approach is described
        2. Why it's relevant (based on the high confidence score)
        3. How it could be applied
        
        Keep it concise but informative.
        """
        
        try:
            response = await self.bayesian_engine._make_llm_call(prompt, max_tokens=200)
            return response.strip()
        except Exception as e:
            return f"Error generating summary: {e}"
    
    async def process_massive_file(self, file_path: str, target_domain: str = "uncertainty_methodology") -> Dict[str, Any]:
        """
        Process a massive file systematically
        """
        print(f"\n🔍 Processing Massive File: {file_path}")
        print("=" * 60)
        
        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return {"error": str(e)}
        
        filename = Path(file_path).stem
        
        print(f"📊 File Stats:")
        print(f"   Size: {len(text):,} characters")
        print(f"   Words: {len(text.split()):,}")
        print(f"   Lines: {text.count(chr(10)):,}")
        
        # Chunk the text
        chunks = self.chunk_text_intelligently(text, filename)
        
        # Process chunks in batches to manage API rate limits
        batch_size = 5  # Process 5 chunks at a time
        all_insights = []
        
        print(f"\n🔄 Processing {len(chunks)} chunks in batches of {batch_size}...")
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            print(f"   Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
            
            # Process batch
            batch_insights = []
            for chunk in batch:
                insights = await self.analyze_chunk_for_insights(chunk, target_domain)
                batch_insights.extend(insights)
                
                # Brief pause to respect rate limits
                await asyncio.sleep(1)
            
            all_insights.extend(batch_insights)
            print(f"   ✅ Extracted {len(batch_insights)} insights from batch")
        
        # Compile results
        results = {
            "filename": filename,
            "file_path": file_path,
            "processing_stats": {
                "total_chars": len(text),
                "total_words": len(text.split()),
                "chunks_created": len(chunks),
                "chunks_processed": len(chunks),
                "insights_extracted": len(all_insights),
                "processing_time": time.time()
            },
            "insights": [
                {
                    "summary": insight.summary,
                    "confidence": insight.confidence,
                    "relevance_score": insight.relevance_score,
                    "source_chunk": insight.source_chunk,
                    "methodology": insight.methodology,
                    "content_preview": insight.content
                }
                for insight in all_insights
            ],
            "top_insights": sorted(
                all_insights, 
                key=lambda x: x.confidence * x.relevance_score, 
                reverse=True
            )[:10]  # Top 10 most confident and relevant insights
        }
        
        # Store results
        self.extracted_insights.extend(all_insights)
        self.processed_chunks.extend(chunks)
        
        print(f"\n✅ Processing Complete!")
        print(f"   Insights Extracted: {len(all_insights)}")
        print(f"   Average Confidence: {sum(i.confidence for i in all_insights) / len(all_insights) if all_insights else 0:.3f}")
        print(f"   High-Confidence Insights (>0.8): {sum(1 for i in all_insights if i.confidence > 0.8)}")
        
        return results
    
    async def process_paul_davis_collection(self, notes_dir: str = "/home/brian/projects/Digimons/paul_davis_notes") -> Dict[str, Any]:
        """
        Process entire Paul Davis notes collection
        """
        print("🎯 Processing Paul Davis Notes Collection")
        print("=" * 70)
        
        notes_path = Path(notes_dir)
        txt_files = list(notes_path.glob("*.txt"))
        
        print(f"Found {len(txt_files)} text files to process")
        
        # Sort by size (smallest first for testing)
        txt_files.sort(key=lambda x: x.stat().st_size)
        
        collection_results = {
            "collection_summary": {
                "total_files": len(txt_files),
                "total_size": sum(f.stat().st_size for f in txt_files),
                "processing_start": time.time()
            },
            "file_results": {},
            "aggregated_insights": []
        }
        
        # Process each file
        for i, file_path in enumerate(txt_files, 1):
            print(f"\n📁 File {i}/{len(txt_files)}: {file_path.name}")
            print(f"   Size: {file_path.stat().st_size / 1024:.1f} KB")
            
            file_results = await self.process_massive_file(str(file_path))
            collection_results["file_results"][file_path.name] = file_results
            
            # Add to aggregated insights
            if "insights" in file_results:
                collection_results["aggregated_insights"].extend(file_results["insights"])
        
        # Generate collection-level summary
        all_insights = collection_results["aggregated_insights"]
        collection_results["collection_summary"].update({
            "processing_end": time.time(),
            "total_insights": len(all_insights),
            "avg_confidence": sum(i["confidence"] for i in all_insights) / len(all_insights) if all_insights else 0,
            "high_confidence_count": sum(1 for i in all_insights if i["confidence"] > 0.8),
            "top_insights": sorted(all_insights, key=lambda x: x["confidence"] * x["relevance_score"], reverse=True)[:20]
        })
        
        return collection_results
    
    def generate_processing_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown report of processing results"""
        
        report = f"""# Paul Davis Notes - Systematic Analysis Report

## Collection Overview
- **Total Files Processed**: {results['collection_summary']['total_files']}
- **Total Data Size**: {results['collection_summary']['total_size'] / 1024:.1f} KB
- **Total Insights Extracted**: {results['collection_summary']['total_insights']}
- **Average Confidence**: {results['collection_summary']['avg_confidence']:.3f}
- **High-Confidence Insights**: {results['collection_summary']['high_confidence_count']}

## File-by-File Summary

"""
        
        for filename, file_result in results["file_results"].items():
            if "error" not in file_result:
                stats = file_result["processing_stats"]
                insights_count = stats["insights_extracted"]
                
                report += f"""### {filename}
- **Size**: {stats['total_chars']:,} characters, {stats['total_words']:,} words
- **Chunks**: {stats['chunks_created']} intelligent chunks
- **Insights**: {insights_count} extracted
- **Key Findings**: {"High-value content" if insights_count > 10 else "Moderate content" if insights_count > 5 else "Limited insights"}

"""
        
        # Top insights across collection
        report += "## Top 10 Most Significant Insights\n\n"
        
        top_insights = results['collection_summary']['top_insights'][:10]
        for i, insight in enumerate(top_insights, 1):
            report += f"""### {i}. {insight['source_chunk']}
**Confidence**: {insight['confidence']:.3f} | **Relevance**: {insight['relevance_score']:.2f}

{insight['summary']}

---

"""
        
        return report

# Test function
async def test_massive_text_processing():
    """Test the massive text processing approach"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key available")
        return
    
    processor = MassiveTextProcessor(api_key)
    
    # Start with a smaller file for testing
    test_file = "/home/brian/projects/Digimons/paul_davis_notes/mrmpm.txt"
    
    print("🧪 Testing Massive Text Processing with smaller file...")
    results = await processor.process_massive_file(test_file)
    
    # Save test results
    output_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test/analysis")
    
    with open(output_dir / "test_processing_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to test_processing_results.json")
    print(f"Insights found: {len(results.get('insights', []))}")
    
    return results

if __name__ == "__main__":
    # Run test
    test_results = asyncio.run(test_massive_text_processing())