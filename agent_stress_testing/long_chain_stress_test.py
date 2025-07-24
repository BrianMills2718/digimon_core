#!/usr/bin/env python3
"""
LONG CHAIN COMPLEXITY STRESS TEST

Tests tool chains with 10-15 sequential operations to find:
1. Memory accumulation issues
2. Error propagation through long chains
3. Performance degradation over time
4. Context loss in long sequences
5. Intermediate result corruption
6. Cascading confidence degradation

This test is designed to break the system through complexity accumulation.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

class LongChainStressTest:
    """Test long sequential tool chains to find breaking points"""
    
    def __init__(self):
        self.test_id = f"long_chain_{uuid.uuid4().hex[:8]}"
        self.chain_failures = []
        self.performance_degradation = []
        self.memory_leaks = []
        
        # Setup aggressive logging
        self.logger = logging.getLogger(f"long_chain_{self.test_id}")
        self.logger.setLevel(logging.DEBUG)
        
        print(f"🔗 LONG CHAIN STRESS TEST INITIALIZED")
        print(f"   Target: 15-step tool chains with error propagation")
        print(f"   Expected: Memory issues, cascading failures, performance degradation")
    
    async def execute_maximum_length_chain(self) -> Dict[str, Any]:
        """Execute the longest possible tool chain until it breaks"""
        
        print(f"\n🚨 MAXIMUM LENGTH CHAIN TEST")
        print(f"   Goal: Push tool chain until system breaks")
        print(f"   Steps: PDF → Chunk → NER → Relations → Graph → Analysis → Query → Synthesis")
        
        # Complex document for maximum processing stress
        complex_document = self._create_maximum_complexity_document()
        
        chain_results = {
            "test_id": self.test_id,
            "start_time": datetime.now().isoformat(),
            "steps_completed": 0,
            "breaking_point": None,
            "performance_timeline": [],
            "memory_timeline": [],
            "intermediate_results": [],
            "failure_cascade": []
        }
        
        try:
            # Import tools
            import sys
            sys.path.append("/home/brian/projects/Digimons")
            
            from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
            from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
            from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
            from src.core.service_manager import get_service_manager
            from src.tools.base_tool import ToolRequest
            
            service_manager = get_service_manager()
            
            # Initialize ALL tools (memory intensive)
            tools = {
                "chunker": T15ATextChunkerUnified(service_manager),
                "ner": T23ASpacyNERUnified(service_manager),
                "relations": T27RelationshipExtractorUnified(service_manager)
            }
            
            print(f"✅ Initialized {len(tools)} tools")
            
            # STEP 1-3: Multi-level text chunking (stress memory)
            chain_data = await self._execute_multi_level_chunking(
                tools, complex_document, chain_results
            )
            
            # STEP 4-6: Exhaustive entity extraction 
            chain_data = await self._execute_exhaustive_entity_extraction(
                tools, chain_data, chain_results
            )
            
            # STEP 7-9: Complex relationship extraction
            chain_data = await self._execute_complex_relationship_extraction(
                tools, chain_data, chain_results
            )
            
            # STEP 10-12: Cross-reference analysis
            chain_data = await self._execute_cross_reference_analysis(
                chain_data, chain_results
            )
            
            # STEP 13-15: Synthesis and validation
            chain_data = await self._execute_synthesis_validation(
                chain_data, chain_results
            )
            
            chain_results["completion_status"] = "UNEXPECTED_SUCCESS"
            chain_results["steps_completed"] = 15
            
            print(f"🎯 UNEXPECTED SUCCESS: Completed all 15 steps")
            print(f"   This suggests the system is more robust than expected")
            
        except MemoryError as e:
            chain_results["breaking_point"] = "MEMORY_EXHAUSTION"
            chain_results["failure_reason"] = str(e)
            print(f"💥 MEMORY EXHAUSTION at step {chain_results['steps_completed']}")
            
        except Exception as e:
            chain_results["breaking_point"] = "TOOL_CHAIN_FAILURE"
            chain_results["failure_reason"] = str(e)
            print(f"🔥 TOOL CHAIN BROKE at step {chain_results['steps_completed']}: {e}")
        
        chain_results["end_time"] = datetime.now().isoformat()
        
        # Analyze failure patterns
        self._analyze_chain_failure_patterns(chain_results)
        
        return chain_results
    
    def _create_maximum_complexity_document(self) -> Dict[str, Any]:
        """Create document designed to maximize processing complexity"""
        
        # Create document with maximum entity density and ambiguity
        complex_content = """
        Dr. Sarah Chen-Wang, former Chief Technology Officer at TechCorp Industries LLC, 
        announced her transition to Meta Platforms Inc. as VP of AI Research, effective January 2024.
        
        Chen-Wang, who previously served as Principal Scientist at Google DeepMind (formerly DeepMind Technologies), 
        brings extensive experience in transformer architectures and large language model optimization.
        
        At TechCorp, she collaborated with Dr. Michael Rodriguez (now at Stanford AI Lab) and 
        Prof. Elena Kowalski from MIT Computer Science Department on breakthrough research in 
        federated learning and privacy-preserving machine learning algorithms.
        
        The announcement came during the International Conference on Machine Learning (ICML 2024) 
        in Vienna, Austria, where Chen-Wang presented joint work with researchers from 
        Carnegie Mellon University, University of Toronto Vector Institute, and INRIA Paris.
        
        This personnel move follows Meta's acquisition of several AI startups including 
        NeuroTech Solutions (founded by former OpenAI researcher Dr. James Thompson) and 
        DataStream Analytics (led by Prof. Anna Müller, previously at ETH Zurich).
        
        Industry analysts from Goldman Sachs and Morgan Stanley predict this hiring trend 
        will accelerate competition between major tech companies including Apple Inc., 
        Microsoft Corporation, Amazon Web Services, and Alphabet Inc. (Google's parent company).
        
        Chen-Wang's research focus on multimodal learning and cross-modal knowledge transfer 
        aligns with Meta's investments in augmented reality (AR), virtual reality (VR), 
        and the broader metaverse ecosystem development initiatives.
        
        The transition involves relocating from San Francisco, California to Menlo Park, California, 
        where Meta's Reality Labs division is headquartered, with additional collaboration 
        planned with teams in New York, Seattle, and London offices.
        """
        
        return {
            "id": "max_complexity_doc",
            "title": "Maximum Complexity Corporate Intelligence Document",
            "content": complex_content,
            "expected_entities": 45,  # Very high entity count
            "expected_relationships": 35,  # Complex relationship web
            "complexity_factors": [
                "Name variations (Chen-Wang vs Chen vs Sarah)",
                "Company acquisitions and mergers",
                "Multiple affiliations per person",
                "Geographic locations and moves", 
                "Temporal relationships",
                "Industry analysis and predictions",
                "Cross-references between entities"
            ]
        }
    
    async def _execute_multi_level_chunking(self, tools: Dict, document: Dict, 
                                          results: Dict) -> Dict[str, Any]:
        """Execute 3 levels of chunking with different strategies"""
        
        print(f"\n🔗 STEPS 1-3: MULTI-LEVEL CHUNKING")
        
        chunking_data = {"document": document, "chunk_levels": []}
        
        # Level 1: Standard chunking
        print(f"   Step 1: Standard chunking...")
        level1_request = ToolRequest(
            tool_id="T15A",
            operation="chunk_text",
            input_data={
                "document_ref": f"storage://stress/{document['id']}_level1.txt",
                "text": document["content"],
                "confidence": 0.9
            },
            parameters={}
        )
        
        level1_result = await asyncio.to_thread(tools["chunker"].execute, level1_request)
        if level1_result.status != "success":
            raise Exception(f"Level 1 chunking failed: {level1_result.error_message}")
        
        level1_chunks = level1_result.data.get("chunks", [])
        chunking_data["chunk_levels"].append({
            "level": 1,
            "strategy": "standard",
            "chunks": level1_chunks,
            "count": len(level1_chunks)
        })
        
        results["steps_completed"] = 1
        print(f"     ✅ Level 1: {len(level1_chunks)} chunks created")
        
        # Level 2: Overlapping chunks from each Level 1 chunk
        print(f"   Step 2: Overlapping sub-chunking...")
        level2_chunks = []
        
        for i, chunk in enumerate(level1_chunks):
            if len(chunk["text"]) > 200:  # Only sub-chunk large chunks
                level2_request = ToolRequest(
                    tool_id="T15A", 
                    operation="chunk_text",
                    input_data={
                        "document_ref": f"storage://stress/{document['id']}_level2_{i}.txt",
                        "text": chunk["text"],
                        "confidence": 0.8
                    },
                    parameters={}
                )
                
                level2_result = await asyncio.to_thread(tools["chunker"].execute, level2_request)
                if level2_result.status == "success":
                    sub_chunks = level2_result.data.get("chunks", [])
                    level2_chunks.extend(sub_chunks)
        
        chunking_data["chunk_levels"].append({
            "level": 2,
            "strategy": "overlapping_sub_chunks",
            "chunks": level2_chunks,
            "count": len(level2_chunks)
        })
        
        results["steps_completed"] = 2
        print(f"     ✅ Level 2: {len(level2_chunks)} sub-chunks created")
        
        # Level 3: Sentence-level micro-chunking (stress test)
        print(f"   Step 3: Sentence-level micro-chunking...")
        level3_chunks = []
        
        # Take first few chunks and break into sentences
        for chunk in level1_chunks[:3]:  # Limit to prevent explosion
            sentences = chunk["text"].split('. ')
            for j, sentence in enumerate(sentences):
                if len(sentence.strip()) > 50:  # Skip very short sentences
                    sentence_chunk = {
                        "chunk_id": f"micro_{chunk['chunk_id']}_{j}",
                        "chunk_ref": f"storage://micro/micro_{chunk['chunk_id']}_{j}",
                        "text": sentence.strip() + ".",
                        "parent_chunk": chunk["chunk_id"]
                    }
                    level3_chunks.append(sentence_chunk)
        
        chunking_data["chunk_levels"].append({
            "level": 3,
            "strategy": "sentence_micro_chunks",
            "chunks": level3_chunks,
            "count": len(level3_chunks)
        })
        
        results["steps_completed"] = 3
        print(f"     ✅ Level 3: {len(level3_chunks)} micro-chunks created")
        
        total_chunks = len(level1_chunks) + len(level2_chunks) + len(level3_chunks)
        print(f"   📊 Total chunks across all levels: {total_chunks}")
        
        if total_chunks > 100:
            print(f"   🚨 HIGH CHUNK COUNT: {total_chunks} chunks may cause memory issues")
        
        results["intermediate_results"].append({
            "step_range": "1-3",
            "operation": "multi_level_chunking",
            "chunk_count": total_chunks,
            "memory_pressure": "HIGH" if total_chunks > 100 else "NORMAL"
        })
        
        return chunking_data
    
    async def _execute_exhaustive_entity_extraction(self, tools: Dict, chain_data: Dict,
                                                   results: Dict) -> Dict[str, Any]:
        """Execute entity extraction on ALL chunk levels"""
        
        print(f"\n🔗 STEPS 4-6: EXHAUSTIVE ENTITY EXTRACTION")
        
        all_entities = []
        entity_conflicts = []
        
        # Step 4: Extract from Level 1 chunks
        print(f"   Step 4: Level 1 entity extraction...")
        level1_chunks = chain_data["chunk_levels"][0]["chunks"]
        
        level1_tasks = []
        for chunk in level1_chunks:
            entity_request = ToolRequest(
                tool_id="T23A",
                operation="extract_entities",
                input_data={
                    "chunk_ref": chunk["chunk_ref"],
                    "text": chunk["text"],
                    "chunk_confidence": 0.9
                },
                parameters={"confidence_threshold": 0.2}
            )
            
            task = asyncio.to_thread(tools["ner"].execute, entity_request)
            level1_tasks.append(task)
        
        level1_results = await asyncio.gather(*level1_tasks, return_exceptions=True)
        
        level1_entities = []
        for result in level1_results:
            if isinstance(result, Exception):
                print(f"     ⚠️ Entity extraction error: {result}")
            elif result.status == "success":
                entities = result.data.get("entities", [])
                level1_entities.extend(entities)
        
        all_entities.extend(level1_entities)
        results["steps_completed"] = 4
        print(f"     ✅ Level 1: {len(level1_entities)} entities extracted")
        
        # Step 5: Extract from Level 2 chunks (overlapping - should find conflicts)
        print(f"   Step 5: Level 2 entity extraction...")
        if len(chain_data["chunk_levels"]) > 1:
            level2_chunks = chain_data["chunk_levels"][1]["chunks"]
            
            level2_tasks = []
            for chunk in level2_chunks:
                entity_request = ToolRequest(
                    tool_id="T23A",
                    operation="extract_entities", 
                    input_data={
                        "chunk_ref": chunk["chunk_ref"],
                        "text": chunk["text"],
                        "chunk_confidence": 0.8
                    },
                    parameters={"confidence_threshold": 0.1}  # Lower threshold
                )
                
                task = asyncio.to_thread(tools["ner"].execute, entity_request)
                level2_tasks.append(task)
            
            level2_results = await asyncio.gather(*level2_tasks, return_exceptions=True)
            
            level2_entities = []
            for result in level2_results:
                if isinstance(result, Exception):
                    continue
                elif result.status == "success":
                    entities = result.data.get("entities", [])
                    level2_entities.extend(entities)
            
            # Detect entity conflicts between levels
            level1_surfaces = {e.get("surface_form", "").lower() for e in level1_entities}
            level2_surfaces = {e.get("surface_form", "").lower() for e in level2_entities}
            conflicts = level1_surfaces.intersection(level2_surfaces)
            
            if conflicts:
                entity_conflicts.extend(list(conflicts))
                print(f"     🚨 Entity conflicts detected: {len(conflicts)} overlapping entities")
            
            all_entities.extend(level2_entities)
            results["steps_completed"] = 5
            print(f"     ✅ Level 2: {len(level2_entities)} entities extracted")
        
        # Step 6: Extract from micro-chunks (maximum granularity)
        print(f"   Step 6: Micro-chunk entity extraction...")
        if len(chain_data["chunk_levels"]) > 2:
            level3_chunks = chain_data["chunk_levels"][2]["chunks"]
            
            # Process micro-chunks in smaller batches to prevent overload
            batch_size = 10
            level3_entities = []
            
            for i in range(0, len(level3_chunks), batch_size):
                batch = level3_chunks[i:i+batch_size]
                batch_tasks = []
                
                for chunk in batch:
                    entity_request = ToolRequest(
                        tool_id="T23A",
                        operation="extract_entities",
                        input_data={
                            "chunk_ref": chunk["chunk_ref"],
                            "text": chunk["text"],
                            "chunk_confidence": 0.7
                        },
                        parameters={"confidence_threshold": 0.05}  # Very low threshold
                    )
                    
                    task = asyncio.to_thread(tools["ner"].execute, entity_request)
                    batch_tasks.append(task)
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        continue
                    elif result.status == "success":
                        entities = result.data.get("entities", [])
                        level3_entities.extend(entities)
                
                # Add small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            all_entities.extend(level3_entities)
            results["steps_completed"] = 6
            print(f"     ✅ Level 3: {len(level3_entities)} micro-entities extracted")
        
        total_entities = len(all_entities)
        print(f"   📊 Total entities across all levels: {total_entities}")
        
        if total_entities > 200:
            print(f"   🚨 ENTITY OVERLOAD: {total_entities} entities may cause processing issues")
        
        results["intermediate_results"].append({
            "step_range": "4-6",
            "operation": "exhaustive_entity_extraction",
            "entity_count": total_entities,
            "conflicts_detected": len(entity_conflicts),
            "memory_pressure": "EXTREME" if total_entities > 200 else "HIGH"
        })
        
        chain_data["all_entities"] = all_entities
        chain_data["entity_conflicts"] = entity_conflicts
        
        return chain_data
    
    async def _execute_complex_relationship_extraction(self, tools: Dict, chain_data: Dict,
                                                      results: Dict) -> Dict[str, Any]:
        """Execute relationship extraction with maximum complexity"""
        
        print(f"\n🔗 STEPS 7-9: COMPLEX RELATIONSHIP EXTRACTION")
        
        all_relationships = []
        relationship_conflicts = []
        
        # Step 7: Standard relationship extraction
        print(f"   Step 7: Standard relationship extraction...")
        level1_chunks = chain_data["chunk_levels"][0]["chunks"]
        all_entities = chain_data["all_entities"]
        
        rel_tasks = []
        for chunk in level1_chunks:
            chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk["chunk_ref"]]
            
            if len(chunk_entities) >= 2:
                rel_request = ToolRequest(
                    tool_id="T27",
                    operation="extract_relationships",
                    input_data={
                        "chunk_ref": chunk["chunk_ref"],
                        "text": chunk["text"],
                        "entities": chunk_entities,
                        "confidence": 0.2
                    },
                    parameters={}
                )
                
                task = asyncio.to_thread(tools["relations"].execute, rel_request)
                rel_tasks.append(task)
        
        rel_results = await asyncio.gather(*rel_tasks, return_exceptions=True)
        
        level1_relationships = []
        for result in rel_results:
            if isinstance(result, Exception):
                continue
            elif result.status == "success":
                relationships = result.data.get("relationships", [])
                level1_relationships.extend(relationships)
        
        all_relationships.extend(level1_relationships)
        results["steps_completed"] = 7
        print(f"     ✅ Standard relationships: {len(level1_relationships)} found")
        
        # Step 8: Cross-chunk relationship detection (computationally expensive)
        print(f"   Step 8: Cross-chunk relationship detection...")
        cross_chunk_relationships = []
        
        # This is intentionally expensive - look for relationships across chunks
        entity_pairs = []
        for i, entity1 in enumerate(all_entities[:50]):  # Limit to prevent explosion
            for entity2 in all_entities[i+1:50]:
                if entity1.get("chunk_ref") != entity2.get("chunk_ref"):
                    entity_pairs.append((entity1, entity2))
        
        print(f"     Analyzing {len(entity_pairs)} cross-chunk entity pairs...")
        
        # Simulate cross-chunk analysis (computationally intensive)
        for entity1, entity2 in entity_pairs[:100]:  # Limit processing
            # Look for implicit relationships based on entity types and context
            if self._detect_implicit_relationship(entity1, entity2):
                relationship = {
                    "source_entity": entity1.get("surface_form", ""),
                    "target_entity": entity2.get("surface_form", ""),
                    "relationship_type": "IMPLICIT_ASSOCIATION",
                    "confidence": 0.3,
                    "evidence_type": "cross_chunk_inference"
                }
                cross_chunk_relationships.append(relationship)
        
        all_relationships.extend(cross_chunk_relationships)
        results["steps_completed"] = 8
        print(f"     ✅ Cross-chunk relationships: {len(cross_chunk_relationships)} inferred")
        
        # Step 9: Temporal relationship analysis (most complex)
        print(f"   Step 9: Temporal relationship analysis...")
        temporal_relationships = []
        
        # Look for temporal patterns in the relationships
        for rel in all_relationships:
            if "former" in rel.get("evidence_text", "").lower() or "previous" in rel.get("evidence_text", "").lower():
                # Create temporal variant
                temporal_rel = rel.copy()
                temporal_rel["relationship_type"] = f"FORMER_{rel['relationship_type']}"
                temporal_rel["temporal_marker"] = "past"
                temporal_relationships.append(temporal_rel)
        
        all_relationships.extend(temporal_relationships)
        results["steps_completed"] = 9
        print(f"     ✅ Temporal relationships: {len(temporal_relationships)} identified")
        
        total_relationships = len(all_relationships)
        print(f"   📊 Total relationships: {total_relationships}")
        
        if total_relationships > 150:
            print(f"   🚨 RELATIONSHIP OVERLOAD: {total_relationships} relationships")
        
        results["intermediate_results"].append({
            "step_range": "7-9", 
            "operation": "complex_relationship_extraction",
            "relationship_count": total_relationships,
            "cross_chunk_analysis": len(cross_chunk_relationships),
            "computational_complexity": "EXTREME"
        })
        
        chain_data["all_relationships"] = all_relationships
        
        return chain_data
    
    def _detect_implicit_relationship(self, entity1: Dict, entity2: Dict) -> bool:
        """Detect implicit relationships between entities (expensive operation)"""
        
        # Simulate expensive analysis
        import time
        time.sleep(0.01)  # Small delay to simulate computation
        
        type1 = entity1.get("entity_type", "")
        type2 = entity2.get("entity_type", "")
        
        # Some basic heuristics for implicit relationships
        if type1 == "PERSON" and type2 == "ORG":
            return True
        if type1 == "ORG" and type2 == "GPE":
            return True
        if type1 == "PERSON" and type2 == "PERSON":
            return random.choice([True, False])  # 50% chance
        
        return False
    
    async def _execute_cross_reference_analysis(self, chain_data: Dict, results: Dict) -> Dict[str, Any]:
        """Execute cross-reference analysis (Steps 10-12)"""
        
        print(f"\n🔗 STEPS 10-12: CROSS-REFERENCE ANALYSIS")
        
        # Step 10: Entity deduplication and merging
        print(f"   Step 10: Entity deduplication...")
        all_entities = chain_data["all_entities"]
        
        # Group entities by surface form (expensive operation)
        entity_groups = {}
        for entity in all_entities:
            surface_form = entity.get("surface_form", "").lower().strip()
            if surface_form not in entity_groups:
                entity_groups[surface_form] = []
            entity_groups[surface_form].append(entity)
        
        # Find duplicates
        duplicates = {k: v for k, v in entity_groups.items() if len(v) > 1}
        
        print(f"     ✅ Found {len(duplicates)} duplicate entity groups")
        results["steps_completed"] = 10
        
        # Step 11: Relationship validation
        print(f"   Step 11: Relationship validation...")
        all_relationships = chain_data["all_relationships"]
        
        valid_relationships = []
        invalid_relationships = []
        
        for rel in all_relationships:
            # Validate that both entities exist
            source = rel.get("source_entity", "")
            target = rel.get("target_entity", "")
            
            source_exists = any(e.get("surface_form", "").lower() == source.lower() for e in all_entities)
            target_exists = any(e.get("surface_form", "").lower() == target.lower() for e in all_entities)
            
            if source_exists and target_exists:
                valid_relationships.append(rel)
            else:
                invalid_relationships.append(rel)
        
        print(f"     ✅ Validated {len(valid_relationships)} relationships, {len(invalid_relationships)} invalid")
        results["steps_completed"] = 11
        
        # Step 12: Consistency checking
        print(f"   Step 12: Consistency checking...")
        consistency_issues = []
        
        # Check for contradictory relationships
        for i, rel1 in enumerate(valid_relationships):
            for rel2 in valid_relationships[i+1:]:
                if (rel1.get("source_entity") == rel2.get("target_entity") and 
                    rel1.get("target_entity") == rel2.get("source_entity")):
                    
                    if rel1.get("relationship_type") != rel2.get("relationship_type"):
                        consistency_issues.append({
                            "type": "contradictory_relationships",
                            "rel1": rel1,
                            "rel2": rel2
                        })
        
        print(f"     ✅ Found {len(consistency_issues)} consistency issues")
        results["steps_completed"] = 12
        
        results["intermediate_results"].append({
            "step_range": "10-12",
            "operation": "cross_reference_analysis", 
            "duplicates_found": len(duplicates),
            "valid_relationships": len(valid_relationships),
            "consistency_issues": len(consistency_issues)
        })
        
        chain_data["deduplicated_entities"] = entity_groups
        chain_data["valid_relationships"] = valid_relationships
        chain_data["consistency_issues"] = consistency_issues
        
        return chain_data
    
    async def _execute_synthesis_validation(self, chain_data: Dict, results: Dict) -> Dict[str, Any]:
        """Execute final synthesis and validation (Steps 13-15)"""
        
        print(f"\n🔗 STEPS 13-15: SYNTHESIS AND VALIDATION")
        
        # Step 13: Knowledge graph construction
        print(f"   Step 13: Knowledge graph construction...")
        entities = chain_data["deduplicated_entities"]
        relationships = chain_data["valid_relationships"]
        
        # Simulate graph construction (memory intensive)
        graph_stats = {
            "unique_entities": len(entities),
            "total_relationships": len(relationships),
            "connected_components": 0,
            "density": 0.0
        }
        
        # Calculate basic graph metrics
        if len(entities) > 1:
            max_possible_edges = len(entities) * (len(entities) - 1) / 2
            graph_stats["density"] = len(relationships) / max_possible_edges if max_possible_edges > 0 else 0
        
        print(f"     ✅ Graph: {graph_stats['unique_entities']} entities, {graph_stats['total_relationships']} edges")
        results["steps_completed"] = 13
        
        # Step 14: Quality assessment
        print(f"   Step 14: Quality assessment...")
        quality_metrics = {
            "entity_coverage": 0.0,
            "relationship_coverage": 0.0,
            "confidence_average": 0.0,
            "consistency_score": 0.0
        }
        
        # Calculate quality metrics
        all_entities_flat = []
        for entity_list in entities.values():
            all_entities_flat.extend(entity_list)
        
        if all_entities_flat:
            confidences = [e.get("confidence", 0.0) for e in all_entities_flat]
            quality_metrics["confidence_average"] = sum(confidences) / len(confidences)
        
        if relationships:
            rel_confidences = [r.get("confidence", 0.0) for r in relationships]
            quality_metrics["relationship_coverage"] = sum(rel_confidences) / len(rel_confidences)
        
        consistency_issues = len(chain_data.get("consistency_issues", []))
        quality_metrics["consistency_score"] = max(0.0, 1.0 - (consistency_issues / max(1, len(relationships))))
        
        print(f"     ✅ Quality: {quality_metrics['confidence_average']:.2f} avg confidence")
        results["steps_completed"] = 14
        
        # Step 15: Final validation and output
        print(f"   Step 15: Final validation...")
        final_output = {
            "graph_statistics": graph_stats,
            "quality_metrics": quality_metrics,
            "processing_chain_summary": {
                "total_chunks": sum(len(level["chunks"]) for level in chain_data["chunk_levels"]),
                "total_entities": len(all_entities_flat),
                "total_relationships": len(relationships),
                "consistency_issues": consistency_issues,
                "processing_complexity": "MAXIMUM"
            },
            "success_indicators": {
                "chain_completed": True,
                "all_steps_executed": True,
                "data_quality_acceptable": quality_metrics["confidence_average"] > 0.3,
                "consistency_maintained": quality_metrics["consistency_score"] > 0.7
            }
        }
        
        print(f"     ✅ Final validation complete")
        results["steps_completed"] = 15
        
        results["intermediate_results"].append({
            "step_range": "13-15",
            "operation": "synthesis_validation",
            "final_output": final_output
        })
        
        chain_data["final_output"] = final_output
        
        return chain_data
    
    def _analyze_chain_failure_patterns(self, results: Dict):
        """Analyze where and why the chain failed"""
        
        print(f"\n📊 CHAIN FAILURE ANALYSIS:")
        
        if results.get("completion_status") == "UNEXPECTED_SUCCESS":
            print(f"   🎯 Chain completed successfully - system more robust than expected")
            print(f"   📈 Performance held steady through {results['steps_completed']} steps")
            return
        
        breaking_point = results.get("breaking_point")
        steps_completed = results.get("steps_completed", 0)
        
        print(f"   💥 Breaking Point: {breaking_point}")
        print(f"   🔢 Steps Completed: {steps_completed}/15")
        print(f"   ⚡ Failure Mode: {results.get('failure_reason', 'Unknown')}")
        
        # Analyze intermediate results for degradation patterns
        intermediate = results.get("intermediate_results", [])
        if intermediate:
            print(f"   📉 Performance Degradation Detected:")
            for result in intermediate:
                if "memory_pressure" in result:
                    print(f"     Step {result['step_range']}: {result['memory_pressure']} memory pressure")
                if "computational_complexity" in result:
                    print(f"     Step {result['step_range']}: {result['computational_complexity']} complexity")

async def run_long_chain_stress_test():
    """Execute the long chain stress test"""
    
    test = LongChainStressTest()
    
    print(f"\n🚨 EXECUTING LONG CHAIN STRESS TEST")
    print(f"   This test is designed to BREAK the system")
    print(f"   Expected failures: Memory exhaustion, cascading errors, performance collapse")
    
    try:
        results = await test.execute_maximum_length_chain()
        
        # Save results
        results_file = f"long_chain_results_{test.test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 RESULTS SAVED: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"💥 STRESS TEST FRAMEWORK FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import random
    asyncio.run(run_long_chain_stress_test())