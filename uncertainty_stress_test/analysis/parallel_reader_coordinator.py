#!/usr/bin/env python3
"""
Coordinate parallel reading of massive Paul Davis documents using subagents
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import math

class ParallelReaderCoordinator:
    """
    Coordinates multiple subagents to read large documents in parallel
    """
    
    def __init__(self):
        self.notes_dir = Path("/home/brian/projects/Digimons/paul_davis_notes")
        self.output_dir = Path("/home/brian/projects/Digimons/uncertainty_stress_test/analysis/parallel_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # Processing configuration
        self.pages_per_chunk = 10  # 10 pages per agent
        self.chars_per_page = 2500  # Approximate characters per page
        self.chars_per_chunk = self.pages_per_chunk * self.chars_per_page  # 25,000 chars per chunk
    
    def chunk_file_for_agents(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Intelligently chunk a file for parallel agent processing
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        total_chars = len(content)
        estimated_pages = total_chars / self.chars_per_page
        num_chunks = math.ceil(total_chars / self.chars_per_chunk)
        
        print(f"📄 {file_path.name}:")
        print(f"   Total: {total_chars:,} chars (~{estimated_pages:.0f} pages)")
        print(f"   Creating: {num_chunks} chunks of ~{self.pages_per_chunk} pages each")
        
        chunks = []
        
        # Split content into chunks, trying to break at paragraph boundaries
        for i in range(num_chunks):
            start_pos = i * self.chars_per_chunk
            end_pos = min((i + 1) * self.chars_per_chunk, total_chars)
            
            # Try to break at paragraph boundary
            if end_pos < total_chars:
                # Look for good break point (paragraph break)
                break_search_start = end_pos - 200
                break_search_end = min(end_pos + 200, total_chars)
                
                best_break = end_pos
                for pos in range(break_search_start, break_search_end):
                    if content[pos:pos+2] == '\n\n':
                        best_break = pos
                        break
                
                end_pos = best_break
            
            chunk_content = content[start_pos:end_pos]
            
            if chunk_content.strip():  # Only create non-empty chunks
                chunk_info = {
                    "file_name": file_path.name,
                    "chunk_id": f"{file_path.stem}_chunk_{i+1:03d}",
                    "chunk_number": i + 1,
                    "total_chunks": num_chunks,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "char_count": len(chunk_content),
                    "estimated_pages": len(chunk_content) / self.chars_per_page,
                    "content": chunk_content
                }
                chunks.append(chunk_info)
        
        print(f"   ✅ Created: {len(chunks)} actual chunks")
        return chunks
    
    def prepare_agent_tasks(self) -> List[Dict[str, Any]]:
        """
        Prepare all agent reading tasks for the entire collection
        """
        all_tasks = []
        
        print("🚀 Preparing Parallel Reading Tasks")
        print("=" * 50)
        
        # Get all txt files, sorted by priority (largest first for testing)
        txt_files = list(self.notes_dir.glob("*.txt"))
        txt_files.sort(key=lambda x: x.stat().st_size, reverse=True)
        
        for file_path in txt_files:
            print(f"\n📖 Processing: {file_path.name} ({file_path.stat().st_size/1024:.1f} KB)")
            
            chunks = self.chunk_file_for_agents(file_path)
            
            for chunk in chunks:
                task = {
                    "task_id": chunk["chunk_id"],
                    "description": f"Read and analyze {chunk['chunk_id']} ({chunk['estimated_pages']:.1f} pages)",
                    "file_info": {
                        "file_name": chunk["file_name"],
                        "chunk_number": chunk["chunk_number"],
                        "total_chunks": chunk["total_chunks"]
                    },
                    "content": chunk["content"],
                    "analysis_instructions": self._create_analysis_instructions(),
                    "expected_output": "methodology_insights_json"
                }
                all_tasks.append(task)
        
        print(f"\n✅ Total Tasks Created: {len(all_tasks)}")
        print(f"📊 Estimated Total Pages: {sum(t['file_info']['total_chunks'] * self.pages_per_chunk for t in all_tasks[:6]):.0f}")
        
        return all_tasks
    
    def _create_analysis_instructions(self) -> str:
        """
        Create detailed instructions for each agent
        """
        return """
        TASK: Read this text chunk thoroughly line by line and extract insights relevant to uncertainty quantification methodology.

        FOCUS AREAS:
        1. **Uncertainty Representation Methods** - How does this text handle uncertainty?
        2. **Validation Approaches** - What validation methods are described?
        3. **Bayesian Methods** - Any Bayesian approaches, priors, inference?
        4. **Evidence Assessment** - How is evidence quality evaluated?
        5. **Multi-method Approaches** - Multiple techniques for handling uncertainty?
        6. **Practical Implementation** - Concrete methods that could be applied?

        EXTRACTION CRITERIA:
        - Look for specific methodological approaches (not just mentions)
        - Extract direct quotes with methodology descriptions
        - Identify novel techniques or frameworks
        - Note practical implementation details
        - Find validation strategies and their effectiveness

        OUTPUT FORMAT (JSON):
        {
            "chunk_summary": "2-3 sentence summary of this chunk's content",
            "methodology_insights": [
                {
                    "type": "uncertainty_representation|validation|bayesian|evidence_assessment|multi_method|implementation",
                    "title": "Brief descriptive title",
                    "description": "Detailed description of the method/approach",
                    "direct_quote": "Relevant direct quote from text",
                    "relevance_to_uncertainty_framework": "How this relates to uncertainty quantification",
                    "implementation_potential": "How this could be practically applied",
                    "confidence": 0.0-1.0
                }
            ],
            "key_terms_found": ["term1", "term2", "term3"],
            "notable_references": ["author1", "author2"] (if any),
            "chunk_relevance_score": 0.0-1.0,
            "requires_followup": true/false,
            "followup_questions": ["question1", "question2"] (if any)
        }

        READ CAREFULLY: This is academic content. Read every paragraph thoroughly. Look for methodological details, not just concept mentions.
        """

def main():
    """
    Prepare all parallel reading tasks
    """
    coordinator = ParallelReaderCoordinator()
    
    # Prepare all tasks
    tasks = coordinator.prepare_agent_tasks()
    
    # Save task configuration
    task_config = {
        "total_tasks": len(tasks),
        "preparation_timestamp": time.time(),
        "processing_config": {
            "pages_per_chunk": coordinator.pages_per_chunk,
            "chars_per_chunk": coordinator.chars_per_chunk,
            "analysis_focus": "uncertainty_methodology"
        },
        "tasks": tasks
    }
    
    config_file = coordinator.output_dir / "parallel_reading_tasks.json"
    with open(config_file, 'w') as f:
        json.dump(task_config, f, indent=2, default=str)
    
    print(f"\n🎯 Task Configuration Complete!")
    print(f"📁 Saved to: {config_file}")
    print(f"📊 Ready to launch {len(tasks)} parallel reading agents")
    
    return tasks

if __name__ == "__main__":
    tasks = main()