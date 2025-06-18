"""
Ontology Storage Service for Academic Traceability (TORC Compliance).
Stores complete ontology generation sessions including conversations, 
generated ontologies, modifications, and usage history.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
from pathlib import Path

from src.ontology_generator import DomainOntology, EntityType, RelationshipType


@dataclass
class OntologySession:
    """Complete record of an ontology generation session."""
    session_id: str
    created_at: datetime
    conversation_history: List[Dict[str, str]]  # Full chat history
    initial_ontology: DomainOntology
    refinements: List[Dict[str, Any]]  # All modifications
    final_ontology: DomainOntology
    generation_parameters: Dict[str, Any]  # Model, temperature, etc.
    validation_results: Optional[Dict[str, Any]] = None
    usage_count: int = 0
    last_used: Optional[datetime] = None


class OntologyStorageService:
    """
    Store and retrieve ontology sessions with complete provenance.
    Ensures academic reproducibility and examinability (TORC compliance).
    """
    
    def __init__(self, db_path: str = "./data/ontology_storage.db"):
        """
        Initialize storage service.
        
        Args:
            db_path: Path to SQLite database for ontology storage
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ontology_sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP,
                    domain_name TEXT,
                    domain_description TEXT,
                    conversation_history TEXT,  -- JSON
                    initial_ontology TEXT,      -- JSON
                    refinements TEXT,           -- JSON array
                    final_ontology TEXT,        -- JSON
                    generation_parameters TEXT,  -- JSON
                    validation_results TEXT,     -- JSON
                    usage_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    checksum TEXT               -- For integrity verification
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ontology_usage (
                    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    used_at TIMESTAMP,
                    usage_type TEXT,  -- 'extraction', 'validation', 'export', etc.
                    usage_context TEXT,  -- JSON with details
                    results_summary TEXT,  -- JSON summary of results
                    FOREIGN KEY (session_id) REFERENCES ontology_sessions(session_id)
                )
            """)
            
            # Index for efficient queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_domain_name ON ontology_sessions(domain_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON ontology_sessions(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_session ON ontology_usage(session_id)")
    
    def save_session(self, session: OntologySession) -> str:
        """
        Save complete ontology session for reproducibility.
        
        Args:
            session: OntologySession with all generation details
            
        Returns:
            session_id for future reference
        """
        # Calculate checksum for integrity
        session_data = {
            "conversation_history": session.conversation_history,
            "initial_ontology": asdict(session.initial_ontology),
            "refinements": session.refinements,
            "final_ontology": asdict(session.final_ontology),
            "generation_parameters": session.generation_parameters
        }
        checksum = hashlib.sha256(json.dumps(session_data, sort_keys=True).encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO ontology_sessions 
                (session_id, created_at, domain_name, domain_description,
                 conversation_history, initial_ontology, refinements, 
                 final_ontology, generation_parameters, validation_results,
                 usage_count, last_used, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.created_at.isoformat(),
                session.final_ontology.domain_name,
                session.final_ontology.domain_description,
                json.dumps(session.conversation_history),
                json.dumps(asdict(session.initial_ontology)),
                json.dumps(session.refinements),
                json.dumps(asdict(session.final_ontology)),
                json.dumps(session.generation_parameters),
                json.dumps(session.validation_results) if session.validation_results else None,
                session.usage_count,
                session.last_used.isoformat() if session.last_used else None,
                checksum
            ))
        
        return session.session_id
    
    def load_session(self, session_id: str) -> Optional[OntologySession]:
        """
        Load complete ontology session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            OntologySession or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM ontology_sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Verify checksum
            stored_checksum = row["checksum"]
            session_data = {
                "conversation_history": json.loads(row["conversation_history"]),
                "initial_ontology": json.loads(row["initial_ontology"]),
                "refinements": json.loads(row["refinements"]),
                "final_ontology": json.loads(row["final_ontology"]),
                "generation_parameters": json.loads(row["generation_parameters"])
            }
            calculated_checksum = hashlib.sha256(
                json.dumps(session_data, sort_keys=True).encode()
            ).hexdigest()
            
            if stored_checksum != calculated_checksum:
                raise ValueError(f"Checksum mismatch for session {session_id}. Data may be corrupted.")
            
            # Reconstruct ontologies
            initial_ont = self._dict_to_ontology(json.loads(row["initial_ontology"]))
            final_ont = self._dict_to_ontology(json.loads(row["final_ontology"]))
            
            return OntologySession(
                session_id=row["session_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                conversation_history=json.loads(row["conversation_history"]),
                initial_ontology=initial_ont,
                refinements=json.loads(row["refinements"]),
                final_ontology=final_ont,
                generation_parameters=json.loads(row["generation_parameters"]),
                validation_results=json.loads(row["validation_results"]) if row["validation_results"] else None,
                usage_count=row["usage_count"],
                last_used=datetime.fromisoformat(row["last_used"]) if row["last_used"] else None
            )
    
    def record_usage(self, session_id: str, usage_type: str, 
                    context: Dict[str, Any], results_summary: Dict[str, Any]):
        """
        Record ontology usage for traceability.
        
        Args:
            session_id: Session being used
            usage_type: Type of usage (extraction, validation, etc.)
            context: Usage context details
            results_summary: Summary of results
        """
        with sqlite3.connect(self.db_path) as conn:
            # Record usage
            conn.execute("""
                INSERT INTO ontology_usage 
                (session_id, used_at, usage_type, usage_context, results_summary)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                usage_type,
                json.dumps(context),
                json.dumps(results_summary)
            ))
            
            # Update usage count and last used
            conn.execute("""
                UPDATE ontology_sessions 
                SET usage_count = usage_count + 1,
                    last_used = ?
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
    
    def list_sessions(self, domain_filter: Optional[str] = None,
                     limit: int = 50) -> List[Dict[str, Any]]:
        """
        List available ontology sessions.
        
        Args:
            domain_filter: Optional domain name filter
            limit: Maximum results
            
        Returns:
            List of session summaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if domain_filter:
                cursor = conn.execute("""
                    SELECT session_id, created_at, domain_name, domain_description,
                           usage_count, last_used
                    FROM ontology_sessions
                    WHERE domain_name LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (f"%{domain_filter}%", limit))
            else:
                cursor = conn.execute("""
                    SELECT session_id, created_at, domain_name, domain_description,
                           usage_count, last_used
                    FROM ontology_sessions
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_usage_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get complete usage history for a session.
        
        Args:
            session_id: Session to query
            
        Returns:
            List of usage records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM ontology_usage
                WHERE session_id = ?
                ORDER BY used_at DESC
            """, (session_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def export_session(self, session_id: str, output_path: str):
        """
        Export complete session for academic sharing.
        
        Args:
            session_id: Session to export
            output_path: Path for JSON export
        """
        session = self.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Get usage history
        usage_history = self.get_usage_history(session_id)
        
        # Create complete export
        export_data = {
            "export_metadata": {
                "exported_at": datetime.now().isoformat(),
                "format_version": "1.0",
                "system": "Super-Digimon Ontology Storage"
            },
            "session": asdict(session),
            "usage_history": usage_history,
            "reproducibility_info": {
                "required_models": ["gemini-2.0-flash-exp", "text-embedding-3-small"],
                "system_requirements": "See Super-Digimon documentation",
                "verification_checksum": session.session_id
            }
        }
        
        # Write export
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def _dict_to_ontology(self, data: Dict[str, Any]) -> DomainOntology:
        """Convert dictionary back to DomainOntology."""
        entity_types = [
            EntityType(**et) for et in data.get("entity_types", [])
        ]
        relationship_types = [
            RelationshipType(**rt) for rt in data.get("relationship_types", [])
        ]
        
        return DomainOntology(
            domain_name=data["domain_name"],
            domain_description=data["domain_description"],
            entity_types=entity_types,
            relationship_types=relationship_types,
            extraction_patterns=data.get("extraction_patterns", []),
            created_by_conversation=data.get("created_by_conversation", "")
        )
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of all stored sessions.
        
        Returns:
            Report of integrity check results
        """
        results = {
            "total_sessions": 0,
            "valid_sessions": 0,
            "corrupted_sessions": [],
            "checked_at": datetime.now().isoformat()
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT session_id FROM ontology_sessions")
            
            for row in cursor.fetchall():
                results["total_sessions"] += 1
                try:
                    session = self.load_session(row["session_id"])
                    if session:
                        results["valid_sessions"] += 1
                except ValueError as e:
                    results["corrupted_sessions"].append({
                        "session_id": row["session_id"],
                        "error": str(e)
                    })
        
        return results