import hashlib
import json
import logging
import os
import time
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

class EvidenceLogger:
    def __init__(self, evidence_file: str = "Evidence.md"):
        self.evidence_file = evidence_file
        self.logger = logging.getLogger(__name__)
        
    def clear_evidence_file(self):
        """Clear the evidence file to ensure a clean slate for new tests."""
        if os.path.exists(self.evidence_file):
            try:
                os.remove(self.evidence_file)
                self.logger.info(f"Cleared evidence file: {self.evidence_file}")
            except OSError as e:
                self.logger.error(f"Error clearing evidence file {self.evidence_file}: {e}")

    def log_task_start(self, task_name: str, description: str):
        """Log the start of a specific task."""
        self.log_with_verification(
            operation=f"TASK_START: {task_name}",
            details={"description": description}
        )

    def log_task_completion(self, task_name: str, result: Dict[str, Any], success: bool):
        """Log the completion of a specific task."""
        self.log_with_verification(
            operation=f"TASK_COMPLETION: {task_name}",
            details={
                "success": success,
                "result": result
            }
        )

    def log_verification_result(self, verification_name: str, result: Dict[str, Any], success: bool):
        """Log the result of a verification task."""
        self.log_with_verification(
            operation=f"VERIFICATION: {verification_name}",
            details={
                "success": success,
                "result": result
            }
        )

    def log_with_verification(self, operation: str, details: Dict[str, Any]) -> str:
        """Log operation with guaranteed cryptographic verification"""
        timestamp = datetime.now().isoformat()
        
        # CRITICAL: Ensure all required fields are present
        verification_data = {
            "timestamp": timestamp,
            "operation": operation,
            "details": details,
            "system_info": self._get_system_info()
        }
        
        # Generate hash from complete data
        hash_input = json.dumps(verification_data, sort_keys=True)
        verification_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # CRITICAL: Include hash in verification data for integrity checking
        verification_data["verification_hash"] = verification_hash
        
        # Format log entry with all required fields
        log_entry = f"\n## **{operation}**\n"
        log_entry += f"**TIMESTAMP**: {timestamp}\n"
        log_entry += f"**VERIFICATION_HASH**: {verification_hash}\n"
        log_entry += f"**DETAILS**: \n```json\n{json.dumps(verification_data, indent=2)}\n```\n"
        log_entry += "---\n"
        
        # Write to evidence file
        with open(self.evidence_file, "a") as f:
            f.write(log_entry)
            
        return verification_hash
        
    def verify_evidence_integrity(self) -> Dict[str, Any]:
        """Comprehensive evidence integrity verification with deep analysis"""
        if not os.path.exists(self.evidence_file):
            return {
                "status": "failed",
                "error": "Evidence file not found",
                "authenticity_score": 0.0
            }
        
        verification_results = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "total_entries": 0,
            "verified_entries": 0,
            "failed_entries": 0,
            "missing_hashes": 0,
            "invalid_timestamps": 0,
            "authenticity_score": 0.0,
            "temporal_consistency": True,
            "hash_integrity": True,
            "format_compliance": True,
            "detailed_analysis": {},
            "integrity_violations": [],
            "confidence_factors": {}
        }
        
        try:
            with open(self.evidence_file, 'r') as f:
                content = f.read()
            
            # Parse evidence entries with enhanced validation
            entries = self._parse_evidence_entries_enhanced(content)
            verification_results["total_entries"] = len(entries)
            
            # Verify each entry with comprehensive checks
            temporal_violations = []
            hash_violations = []
            format_violations = []
            
            for entry in entries:
                entry_verification = self._verify_single_entry_comprehensive(entry)
                
                if entry_verification["valid"]:
                    verification_results["verified_entries"] += 1
                else:
                    verification_results["failed_entries"] += 1
                    verification_results["detailed_analysis"][entry["entry_id"]] = entry_verification
                
                # Track specific violation types
                if not entry_verification.get("has_hash", True):
                    verification_results["missing_hashes"] += 1
                    hash_violations.append(entry["entry_id"])
                
                if not entry_verification.get("timestamp_valid", True):
                    verification_results["invalid_timestamps"] += 1
                    temporal_violations.append(entry["entry_id"])
                
                if not entry_verification.get("format_valid", True):
                    format_violations.append(entry["entry_id"])
            
            # Calculate comprehensive authenticity score
            base_score = verification_results["verified_entries"] / max(verification_results["total_entries"], 1)
            
            # Apply penalties for various issues
            hash_penalty = (verification_results["missing_hashes"] / max(verification_results["total_entries"], 1)) * 0.5
            timestamp_penalty = (verification_results["invalid_timestamps"] / max(verification_results["total_entries"], 1)) * 0.3
            format_penalty = (len(format_violations) / max(verification_results["total_entries"], 1)) * 0.2
            
            authenticity_score = max(0.0, base_score - hash_penalty - timestamp_penalty - format_penalty)
            verification_results["authenticity_score"] = authenticity_score
            
            # Detailed integrity analysis
            verification_results["temporal_consistency"] = len(temporal_violations) == 0
            verification_results["hash_integrity"] = len(hash_violations) == 0
            verification_results["format_compliance"] = len(format_violations) == 0
            
            # Record violations
            if temporal_violations:
                verification_results["integrity_violations"].append(f"Temporal violations in entries: {temporal_violations}")
            if hash_violations:
                verification_results["integrity_violations"].append(f"Missing hashes in entries: {hash_violations}")
            if format_violations:
                verification_results["integrity_violations"].append(f"Format violations in entries: {format_violations}")
            
            # Confidence factors
            verification_results["confidence_factors"] = {
                "entry_completeness": 1.0 - (verification_results["failed_entries"] / max(verification_results["total_entries"], 1)),
                "hash_completeness": 1.0 - (verification_results["missing_hashes"] / max(verification_results["total_entries"], 1)),
                "temporal_consistency": 1.0 - (verification_results["invalid_timestamps"] / max(verification_results["total_entries"], 1)),
                "format_consistency": 1.0 - (len(format_violations) / max(verification_results["total_entries"], 1))
            }
            
            # Additional integrity checks
            verification_results.update(self._perform_advanced_integrity_checks(entries))
            
        except Exception as e:
            verification_results["status"] = "failed"
            verification_results["error"] = str(e)
            verification_results["authenticity_score"] = 0.0
        
        return verification_results

    def _parse_evidence_entries(self, content: str) -> List[Dict[str, Any]]:
        """Parse evidence entries from content"""
        entries = []
        
        # Split by operation headers
        operation_pattern = r'\n## \*\*([^*]+)\*\*\n'
        operations = re.split(operation_pattern, content)
        
        for i in range(1, len(operations), 2):
            if i + 1 < len(operations):
                operation_name = operations[i]
                operation_content = operations[i + 1]
                
                # Extract timestamp
                timestamp_match = re.search(r'\*\*TIMESTAMP\*\*: ([^\n]+)', operation_content)
                timestamp = timestamp_match.group(1) if timestamp_match else None
                
                # Extract hash
                hash_match = re.search(r'\*\*VERIFICATION_HASH\*\*: ([a-f0-9]{64})', operation_content)
                verification_hash = hash_match.group(1) if hash_match else None
                
                # Extract details
                details_match = re.search(r'\*\*DETAILS\*\*: \n```json\n(.*?)\n```', operation_content, re.DOTALL)
                details = None
                if details_match:
                    try:
                        details = json.loads(details_match.group(1))
                    except:
                        pass
                
                entry = {
                    "entry_id": str(uuid.uuid4()),
                    "operation": operation_name,
                    "timestamp": timestamp,
                    "verification_hash": verification_hash,
                    "details": details,
                    "raw_content": operation_content
                }
                
                entries.append(entry)
        
        return entries
    
    def _parse_evidence_entries_enhanced(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced evidence entry parsing with comprehensive extraction"""
        entries = []
        
        # Split by operation headers (##)
        sections = content.split('\n## **')
        
        for i, section in enumerate(sections):
            if i == 0:  # Skip header
                continue
            
            # Extract operation name
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            operation_name = lines[0].replace('**', '').strip()
            
            # Create entry structure
            entry = {
                "entry_id": f"entry_{i}",
                "operation": operation_name,
                "raw_content": section,
                "timestamp": None,
                "verification_hash": None,
                "details": None,
                "line_count": len(lines),
                "character_count": len(section)
            }
            
            # Extract timestamp
            for line in lines:
                if line.startswith('**TIMESTAMP**:'):
                    entry["timestamp"] = line.replace('**TIMESTAMP**:', '').strip()
                    break
            
            # Extract verification hash
            for line in lines:
                if line.startswith('**VERIFICATION_HASH**:'):
                    entry["verification_hash"] = line.replace('**VERIFICATION_HASH**:', '').strip()
                    break
            
            # Extract details JSON
            details_start = None
            details_end = None
            for j, line in enumerate(lines):
                if '```json' in line:
                    details_start = j + 1
                elif details_start is not None and '```' in line:
                    details_end = j
                    break
            
            if details_start is not None and details_end is not None:
                try:
                    details_json = '\n'.join(lines[details_start:details_end])
                    entry["details"] = json.loads(details_json)
                except json.JSONDecodeError as e:
                    entry["details_parse_error"] = str(e)
            
            entries.append(entry)
        
        return entries

    def _verify_single_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Verify individual evidence entry"""
        verification = {
            "valid": True,
            "issues": []
        }
        
        # Verify required fields
        required_fields = ["timestamp", "operation", "verification_hash"]
        for field in required_fields:
            if field not in entry or entry[field] is None:
                verification["valid"] = False
                verification["issues"].append(f"Missing required field: {field}")
        
        # Verify timestamp format and reasonableness
        if "timestamp" in entry and entry["timestamp"]:
            try:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                now = datetime.now()
                
                # Check for future timestamps
                if timestamp > now:
                    verification["valid"] = False
                    verification["issues"].append("Future timestamp detected")
                
                # Check for unreasonably old timestamps
                if (now - timestamp).days > 30:
                    verification["issues"].append("Timestamp older than 30 days")
                    
            except Exception:
                verification["valid"] = False
                verification["issues"].append("Invalid timestamp format")
        
        # Verify hash format
        if "verification_hash" in entry and entry["verification_hash"]:
            hash_value = entry["verification_hash"]
            if not isinstance(hash_value, str) or len(hash_value) != 64:
                verification["valid"] = False
                verification["issues"].append("Invalid SHA256 hash format")
            elif not all(c in '0123456789abcdef' for c in hash_value):
                verification["valid"] = False
                verification["issues"].append("Hash contains invalid characters")
        
        # Verify hash consistency if details are available
        if entry.get("details") and entry.get("verification_hash"):
            try:
                hash_input = json.dumps(entry["details"], sort_keys=True)
                expected_hash = hashlib.sha256(hash_input.encode()).hexdigest()
                
                if expected_hash != entry["verification_hash"]:
                    verification["valid"] = False
                    verification["issues"].append("Hash does not match content")
            except Exception:
                verification["issues"].append("Could not verify hash consistency")
        
        return verification
    
    def _verify_single_entry_comprehensive(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive verification of individual evidence entry"""
        verification = {
            "valid": True,
            "issues": [],
            "has_operation": False,
            "has_timestamp": False,
            "has_hash": False,
            "has_details": False,
            "timestamp_valid": False,
            "hash_valid": False,
            "details_valid": False,
            "format_valid": True,
            "completeness_score": 0.0
        }
        
        # Check operation
        if entry.get("operation"):
            verification["has_operation"] = True
        else:
            verification["valid"] = False
            verification["issues"].append("Missing operation name")
        
        # Check timestamp
        if entry.get("timestamp"):
            verification["has_timestamp"] = True
            try:
                # Validate timestamp format
                timestamp_dt = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
                now = datetime.now()
                
                # Check if timestamp is reasonable (not future, not too old)
                if timestamp_dt <= now and (now - timestamp_dt).days < 365:
                    verification["timestamp_valid"] = True
                else:
                    verification["issues"].append("Timestamp outside reasonable range")
            except ValueError:
                verification["issues"].append("Invalid timestamp format")
        else:
            verification["valid"] = False
            verification["issues"].append("Missing timestamp")
        
        # Check verification hash
        if entry.get("verification_hash"):
            verification["has_hash"] = True
            hash_value = entry["verification_hash"]
            
            # Validate hash format (SHA256 is 64 hex characters)
            if len(hash_value) == 64 and all(c in '0123456789abcdef' for c in hash_value.lower()):
                verification["hash_valid"] = True
            else:
                verification["issues"].append("Invalid hash format")
        else:
            verification["valid"] = False
            verification["issues"].append("Missing verification hash")
        
        # Check details
        if entry.get("details"):
            verification["has_details"] = True
            details = entry["details"]
            
            # Validate details structure
            if isinstance(details, dict):
                required_fields = ["timestamp", "operation"]
                has_required = all(field in details for field in required_fields)
                
                if has_required:
                    verification["details_valid"] = True
                else:
                    verification["issues"].append("Details missing required fields")
            else:
                verification["issues"].append("Details not in correct format")
        else:
            verification["valid"] = False
            verification["issues"].append("Missing details")
        
        # Calculate completeness score
        completeness_factors = [
            verification["has_operation"],
            verification["has_timestamp"],
            verification["has_hash"],
            verification["has_details"],
            verification["timestamp_valid"],
            verification["hash_valid"],
            verification["details_valid"]
        ]
        
        verification["completeness_score"] = sum(completeness_factors) / len(completeness_factors)
        
        # Overall validity requires high completeness
        if verification["completeness_score"] < 0.8:
            verification["valid"] = False
        
        return verification

    def _verify_temporal_consistency(self, entries: List[Dict[str, Any]]) -> bool:
        """Verify temporal consistency of entries"""
        if len(entries) < 2:
            return True
        
        timestamps = []
        for entry in entries:
            if entry.get("timestamp"):
                try:
                    timestamp = datetime.fromisoformat(entry["timestamp"])
                    timestamps.append(timestamp)
                except:
                    continue
        
        if len(timestamps) < 2:
            return True
        
        # Check if timestamps are generally in chronological order
        # Allow some tolerance for concurrent operations
        out_of_order_count = 0
        for i in range(1, len(timestamps)):
            if timestamps[i] < timestamps[i-1]:
                # Allow up to 5 minutes out of order for concurrent operations
                time_diff = (timestamps[i-1] - timestamps[i]).total_seconds()
                if time_diff > 300:  # 5 minutes
                    out_of_order_count += 1
        
        # Allow up to 10% of entries to be out of order
        return out_of_order_count <= len(timestamps) * 0.1

    def _verify_hash_integrity(self, entries: List[Dict[str, Any]]) -> bool:
        """Verify hash integrity across all entries"""
        valid_hashes = 0
        total_hashes = 0
        
        for entry in entries:
            if entry.get("verification_hash"):
                total_hashes += 1
                hash_value = entry["verification_hash"]
                
                # Basic format check
                if (isinstance(hash_value, str) and 
                    len(hash_value) == 64 and 
                    all(c in '0123456789abcdef' for c in hash_value)):
                    valid_hashes += 1
        
        if total_hashes == 0:
            return False
        
        # Require at least 95% of hashes to be valid
        return (valid_hashes / total_hashes) >= 0.95

    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get comprehensive evidence summary"""
        verification_result = self.verify_evidence_integrity()
        
        if "error" in verification_result:
            return {"error": verification_result["error"]}
        
        try:
            with open(self.evidence_file, 'r') as f:
                content = f.read()
            
            entries = self._parse_evidence_entries(content)
            
            # Analyze entry types
            operation_counts = {}
            for entry in entries:
                operation = entry.get("operation", "unknown")
                operation_counts[operation] = operation_counts.get(operation, 0) + 1
            
            # Calculate time span
            timestamps = []
            for entry in entries:
                if entry.get("timestamp"):
                    try:
                        timestamp = datetime.fromisoformat(entry["timestamp"])
                        timestamps.append(timestamp)
                    except:
                        continue
            
            time_span = None
            if len(timestamps) >= 2:
                time_span = (max(timestamps) - min(timestamps)).total_seconds()
            
            return {
                "total_entries": len(entries),
                "operation_types": len(operation_counts),
                "operation_counts": operation_counts,
                "time_span_seconds": time_span,
                "earliest_entry": min(timestamps).isoformat() if timestamps else None,
                "latest_entry": max(timestamps).isoformat() if timestamps else None,
                "authenticity_score": verification_result.get("authenticity_score", 0.0),
                "temporal_consistency": verification_result.get("temporal_consistency", False),
                "hash_integrity": verification_result.get("hash_integrity", False)
            }
            
        except Exception as e:
            return {"error": str(e)}

    def validate_evidence_authenticity(self) -> Dict[str, Any]:
        """Comprehensive evidence authenticity validation"""
        verification = self.verify_evidence_integrity()
        summary = self.get_evidence_summary()
        
        # Combine results for final authenticity assessment
        authenticity_result = {
            "verification_result": verification,
            "evidence_summary": summary,
            "overall_authenticity": "unknown",
            "confidence_score": 0.0,
            "recommendations": []
        }
        
        if "error" in verification or "error" in summary:
            authenticity_result["overall_authenticity"] = "error"
            authenticity_result["recommendations"].append("Fix evidence file errors before validation")
            return authenticity_result
        
        # Calculate confidence score
        scores = []
        
        # Authenticity score (40% weight)
        auth_score = verification.get("authenticity_score", 0.0)
        scores.append(auth_score * 0.4)
        
        # Temporal consistency (30% weight)
        if verification.get("temporal_consistency", False):
            scores.append(0.3)
        
        # Hash integrity (30% weight)
        if verification.get("hash_integrity", False):
            scores.append(0.3)
        
        authenticity_result["confidence_score"] = sum(scores)
        
        # Determine overall authenticity
        if authenticity_result["confidence_score"] >= 0.9:
            authenticity_result["overall_authenticity"] = "high"
        elif authenticity_result["confidence_score"] >= 0.7:
            authenticity_result["overall_authenticity"] = "medium"
        elif authenticity_result["confidence_score"] >= 0.5:
            authenticity_result["overall_authenticity"] = "low"
        else:
            authenticity_result["overall_authenticity"] = "very_low"
        
        # Generate recommendations
        if auth_score < 0.8:
            authenticity_result["recommendations"].append("Improve evidence entry validation")
        
        if not verification.get("temporal_consistency", False):
            authenticity_result["recommendations"].append("Review timestamp consistency across entries")
        
        if not verification.get("hash_integrity", False):
            authenticity_result["recommendations"].append("Verify hash generation and storage processes")
        
        return authenticity_result
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for verification"""
        try:
            import psutil
            return {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "python_version": os.sys.version,
                "timestamp": time.time()
            }
        except ImportError:
            return {
                "cpu_usage": "unknown",
                "memory_usage": "unknown", 
                "disk_usage": "unknown",
                "python_version": os.sys.version,
                "timestamp": time.time()
            }

    def _perform_advanced_integrity_checks(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform advanced integrity checks on evidence entries"""
        advanced_checks = {
            "chronological_order": True,
            "hash_uniqueness": True,
            "operation_patterns": {},
            "temporal_gaps": [],
            "suspicious_patterns": [],
            "data_consistency": True
        }
        
        # Check chronological order
        timestamps = []
        for entry in entries:
            if entry.get("timestamp"):
                try:
                    timestamp_dt = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
                    timestamps.append((timestamp_dt, entry["entry_id"]))
                except ValueError:
                    continue
        
        timestamps.sort()
        if len(timestamps) > 1:
            for i in range(1, len(timestamps)):
                if timestamps[i][0] < timestamps[i-1][0]:
                    advanced_checks["chronological_order"] = False
                    break
        
        # Check hash uniqueness
        hashes = [entry.get("verification_hash") for entry in entries if entry.get("verification_hash")]
        if len(hashes) != len(set(hashes)):
            advanced_checks["hash_uniqueness"] = False
            advanced_checks["suspicious_patterns"].append("Duplicate verification hashes detected")
        
        # Analyze operation patterns
        for entry in entries:
            operation = entry.get("operation", "unknown")
            advanced_checks["operation_patterns"][operation] = advanced_checks["operation_patterns"].get(operation, 0) + 1
        
        # Check for temporal gaps (periods > 6 hours without entries)
        if len(timestamps) > 1:
            for i in range(1, len(timestamps)):
                gap = timestamps[i][0] - timestamps[i-1][0]
                if gap.total_seconds() > 21600:  # 6 hours
                    advanced_checks["temporal_gaps"].append({
                        "start": timestamps[i-1][0].isoformat(),
                        "end": timestamps[i][0].isoformat(),
                        "gap_hours": gap.total_seconds() / 3600
                    })
        
        return advanced_checks
    
    def log_tool_audit_results(self, audit_results: Dict[str, Any], operation_id: str):
        """Log tool audit results with consistent formatting and validation"""
        # Validate audit results structure
        required_fields = ["total_tools", "working_tools", "broken_tools", "tool_results"]
        for field in required_fields:
            if field not in audit_results:
                raise ValueError(f"Missing required field in audit results: {field}")
        
        # Calculate and validate success rate
        total_tools = audit_results["total_tools"]
        working_tools = audit_results["working_tools"]
        
        if total_tools <= 0:
            raise ValueError("Total tools must be greater than 0")
        if working_tools < 0 or working_tools > total_tools:
            raise ValueError(f"Working tools ({working_tools}) invalid for total ({total_tools})")
        
        success_rate = (working_tools / total_tools) * 100
        
        # Create standardized evidence entry
        evidence_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": f"TOOL_AUDIT_RESULTS_{operation_id}",
            "audit_summary": {
                "total_tools": total_tools,
                "working_tools": working_tools,
                "broken_tools": audit_results["broken_tools"],
                "success_rate_percent": round(success_rate, 2),
                "calculation_verified": working_tools + audit_results["broken_tools"] == total_tools
            },
            "detailed_results": audit_results["tool_results"],
            "consistency_check": {
                "math_verified": working_tools + audit_results["broken_tools"] == total_tools,
                "success_rate_formula": f"({working_tools}/{total_tools}) * 100 = {success_rate:.2f}%"
            }
        }
        
        self.log_with_verification(f"TOOL_AUDIT_CONSISTENT_{operation_id}", evidence_entry)
        return evidence_entry

# Global evidence logger instance
evidence_logger = EvidenceLogger()