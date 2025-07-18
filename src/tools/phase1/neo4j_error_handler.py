"""Neo4j Error Handler - Proper error handling for Neo4j operations

Implements the NO MOCKS policy from CLAUDE.md:
- When Neo4j is down, fail clearly - don't pretend to work
- Provide actionable error messages
- Never return fake data
"""

from typing import Dict, Any, Optional


class Neo4jErrorHandler:
    """Handles Neo4j errors according to NO MOCKS policy."""
    
    @staticmethod
    def create_connection_error(operation: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        """Create error response for Neo4j connection failures."""
        error_msg = str(error) if error else "Neo4j connection unavailable"
        
        return {
            "status": "error",
            "error": "Neo4j database unavailable",
            "message": f"Cannot perform {operation} without database connection",
            "details": error_msg,
            "recovery_suggestions": [
                "Ensure Neo4j is running on port 7687",
                "Verify credentials in configuration", 
                "Check network connectivity to database",
                "Run: docker ps | grep neo4j to check container status"
            ],
            "operation": operation
        }
    
    @staticmethod
    def create_operation_error(operation: str, error: Exception) -> Dict[str, Any]:
        """Create error response for Neo4j operation failures."""
        error_msg = str(error)
        error_lower = error_msg.lower()
        
        # Provide specific recovery suggestions based on error type
        if "constraint" in error_lower:
            suggestions = [
                "Check for duplicate entities or relationships",
                "Verify data integrity constraints",
                "Review Neo4j constraint definitions"
            ]
        elif "memory" in error_lower or "heap" in error_lower:
            suggestions = [
                "Increase Neo4j heap memory allocation",
                "Reduce batch size for operations",
                "Check available system memory"
            ]
        elif "timeout" in error_lower:
            suggestions = [
                "Increase query timeout settings",
                "Optimize query for better performance",
                "Check Neo4j server load"
            ]
        else:
            suggestions = [
                "Check Neo4j logs for detailed error information",
                "Verify query syntax and parameters",
                "Ensure database is not in read-only mode"
            ]
        
        return {
            "status": "error",
            "error": f"{operation} operation failed",
            "message": error_msg,
            "recovery_suggestions": suggestions,
            "operation": operation
        }
    
    @staticmethod
    def check_driver_available(driver) -> Optional[Dict[str, Any]]:
        """Check if Neo4j driver is available and return error if not."""
        if driver is None:
            return Neo4jErrorHandler.create_connection_error("database operation")
        
        # Test connection is alive
        try:
            with driver.session() as session:
                session.run("RETURN 1")
            return None  # Connection is good
        except Exception as e:
            return Neo4jErrorHandler.create_connection_error("database operation", e)