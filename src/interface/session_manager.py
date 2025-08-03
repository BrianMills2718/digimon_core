"""
Session Manager for Natural Language Interface
Manages conversation sessions and context
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class Interaction:
    """Single question-answer interaction"""
    question: str
    response: Any  # NLResponse object
    timestamp: float
    confidence: float = 0.0

@dataclass 
class SessionContext:
    """Context for a conversation session"""
    session_id: str
    created_at: float
    last_activity: float
    interactions: List[Interaction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class SessionManager:
    """Manage conversation sessions and context"""
    
    def __init__(self, max_sessions: int = 100, session_timeout: float = 3600):
        self.sessions: Dict[str, SessionContext] = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout  # 1 hour default
        
    def create_session(self, session_id: str = None) -> str:
        """Create a new session"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        current_time = time.time()
        
        session_context = SessionContext(
            session_id=session_id,
            created_at=current_time,
            last_activity=current_time,
            interactions=[],
            metadata={}
        )
        
        self.sessions[session_id] = session_context
        
        # Clean up old sessions if needed
        self._cleanup_sessions()
        
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def add_interaction(self, session_id: str, question: str, response) -> None:
        """Add question-answer interaction to session"""
        
        # Create session if it doesn't exist
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        session = self.sessions[session_id]
        
        # Extract confidence from response
        confidence = 0.5
        if hasattr(response, 'confidence'):
            confidence = response.confidence
        
        interaction = Interaction(
            question=question,
            response=response,
            timestamp=time.time(),
            confidence=confidence
        )
        
        session.interactions.append(interaction)
        session.last_activity = time.time()
        
        logger.debug(f"Added interaction to session {session_id}: {question[:50]}...")
    
    def get_session_interactions(self, session_id: str) -> List[Interaction]:
        """Get all interactions for a session"""
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id].interactions
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get complete context for a session"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        
        return {
            'session_id': session.session_id,
            'created_at': session.created_at,
            'last_activity': session.last_activity,
            'interaction_count': len(session.interactions),
            'interactions': session.interactions,
            'metadata': session.metadata,
            'duration': time.time() - session.created_at,
            'active': self._is_session_active(session)
        }
    
    def get_recent_context(self, session_id: str, max_interactions: int = 3) -> List[Interaction]:
        """Get recent interactions for context"""
        interactions = self.get_session_interactions(session_id)
        return interactions[-max_interactions:] if interactions else []
    
    def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> None:
        """Update session metadata"""
        if session_id in self.sessions:
            self.sessions[session_id].metadata.update(metadata)
            self.sessions[session_id].last_activity = time.time()
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary statistics for a session"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        interactions = session.interactions
        
        if not interactions:
            return {
                'session_id': session_id,
                'interaction_count': 0,
                'average_confidence': 0.0,
                'topics_discussed': [],
                'session_duration': time.time() - session.created_at
            }
        
        # Calculate statistics
        total_confidence = sum(i.confidence for i in interactions)
        avg_confidence = total_confidence / len(interactions)
        
        # Extract topics from questions (simple keyword extraction)
        topics = self._extract_topics_from_interactions(interactions)
        
        return {
            'session_id': session_id,
            'interaction_count': len(interactions),
            'average_confidence': avg_confidence,
            'topics_discussed': topics,
            'session_duration': time.time() - session.created_at,
            'first_question': interactions[0].question if interactions else None,
            'last_question': interactions[-1].question if interactions else None
        }
    
    def _extract_topics_from_interactions(self, interactions: List[Interaction]) -> List[str]:
        """Extract topics from interaction questions"""
        topics = set()
        
        # Simple keyword-based topic extraction
        topic_keywords = {
            'entities': ['who', 'entities', 'people', 'organizations'],
            'relationships': ['relate', 'connect', 'relationship', 'between'],
            'themes': ['themes', 'topics', 'subjects', 'about'],
            'summary': ['summary', 'summarize', 'overview', 'main'],
            'analysis': ['analyze', 'analysis', 'examine', 'study']
        }
        
        for interaction in interactions:
            question_lower = interaction.question.lower()
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    topics.add(topic)
        
        return list(topics)
    
    def _is_session_active(self, session: SessionContext) -> bool:
        """Check if session is still active"""
        return (time.time() - session.last_activity) < self.session_timeout
    
    def _cleanup_sessions(self) -> None:
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if (current_time - session.last_activity) > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        # Also clean up oldest sessions if we exceed max_sessions
        if len(self.sessions) > self.max_sessions:
            # Sort by last activity and remove oldest
            sorted_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1].last_activity
            )
            
            sessions_to_remove = len(self.sessions) - self.max_sessions
            for i in range(sessions_to_remove):
                session_id = sorted_sessions[i][0]
                del self.sessions[session_id]
                logger.info(f"Cleaned up old session to maintain limit: {session_id}")
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        active_sessions = []
        
        for session_id, session in self.sessions.items():
            if self._is_session_active(session):
                active_sessions.append({
                    'session_id': session_id,
                    'created_at': session.created_at,
                    'last_activity': session.last_activity,
                    'interaction_count': len(session.interactions),
                    'duration': time.time() - session.created_at
                })
        
        return sorted(active_sessions, key=lambda x: x['last_activity'], reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session manager statistics"""
        active_count = len([s for s in self.sessions.values() if self._is_session_active(s)])
        total_interactions = sum(len(s.interactions) for s in self.sessions.values())
        
        return {
            'total_sessions': len(self.sessions),
            'active_sessions': active_count,
            'expired_sessions': len(self.sessions) - active_count,
            'total_interactions': total_interactions,
            'average_interactions_per_session': total_interactions / len(self.sessions) if self.sessions else 0,
            'session_timeout': self.session_timeout,
            'max_sessions': self.max_sessions
        }