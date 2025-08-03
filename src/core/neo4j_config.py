from src.core.standard_config import get_database_uri
"""
Neo4j Configuration Management for KGAS

Handles automatic Neo4j connection with fallback strategies:
1. Try environment variables
2. Try .env file
3. Try common Docker containers
4. Provide clear setup instructions if all fail
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable
import subprocess
import json

logger = logging.getLogger(__name__)


class Neo4jConfig:
    """Manages Neo4j configuration and connection"""
    
    # Common Neo4j container names to check
    COMMON_CONTAINER_NAMES = [
        "neo4j",
        "kgas-neo4j",
        "qualitative_coding_neo4j",
        "test-neo4j",
        "neo4j-graphrag"
    ]
    
    # Security Note: Hardcoded passwords removed for security compliance.
    # Use environment variables, .env files, or secure credential management instead.
    COMMON_PASSWORDS = []  # Deliberately empty for security
    
    def __init__(self):
        self.uri = None
        self.user = None
        self.password = None
        self.driver = None
        self.connection_info = {}
        
    def connect(self) -> bool:
        """
        Attempt to connect to Neo4j using multiple strategies.
        Returns True if successful, False otherwise.
        """
        # Strategy 1: Try environment variables
        if self._try_env_connection():
            return True
            
        # Strategy 2: Try .env file
        if self._try_dotenv_connection():
            return True
            
        # Strategy 3: Try Docker containers
        if self._try_docker_connection():
            return True
            
        # Strategy 4: Try localhost with common passwords
        if self._try_localhost_connection():
            return True
            
        # All strategies failed
        self._provide_setup_instructions()
        return False
    
    def _try_env_connection(self) -> bool:
        """Try connection using environment variables"""
        logger.info("Trying Neo4j connection from environment variables...")
        
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        
        if uri and password:
            if self._test_connection(uri, user, password):
                self.connection_info["source"] = "environment"
                logger.info("✅ Connected using environment variables")
                return True
                
        return False
    
    def _try_dotenv_connection(self) -> bool:
        """Try connection using .env file"""
        logger.info("Trying Neo4j connection from .env file...")
        
        env_path = Path(".env")
        if env_path.exists():
            # Parse .env file
            env_vars = {}
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
            
            uri = env_vars.get("NEO4J_URI", get_database_uri())
            user = env_vars.get("NEO4J_USER", "neo4j")
            password = env_vars.get("NEO4J_PASSWORD")
            
            if password and self._test_connection(uri, user, password):
                self.connection_info["source"] = ".env file"
                logger.info("✅ Connected using .env file")
                return True
                
        return False
    
    def _try_docker_connection(self) -> bool:
        """Try to find and connect to running Docker containers"""
        logger.info("Looking for Neo4j Docker containers...")
        
        try:
            # Get running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        containers.append(json.loads(line))
                
                # Look for Neo4j containers
                for container in containers:
                    container_name = container.get("Names", "")
                    container_image = container.get("Image", "")
                    
                    if "neo4j" in container_image.lower() or any(name in container_name for name in self.COMMON_CONTAINER_NAMES):
                        logger.info(f"Found Neo4j container: {container_name}")
                        
                        # Try to get password from container environment
                        password = self._get_container_password(container_name)
                        if password:
                            uri = get_database_uri()
                            user = "neo4j"
                            
                            if self._test_connection(uri, user, password):
                                self.connection_info["source"] = f"Docker container: {container_name}"
                                self.connection_info["container"] = container_name
                                logger.info(f"✅ Connected to Docker container: {container_name}")
                                return True
                                
        except Exception as e:
            logger.warning(f"Docker inspection failed: {e}")
            
        return False
    
    def _get_container_password(self, container_name: str) -> Optional[str]:
        """Extract password from Docker container configuration"""
        try:
            result = subprocess.run(
                ["docker", "inspect", container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                config = json.loads(result.stdout)[0]
                env_vars = config.get("Config", {}).get("Env", [])
                
                for env_var in env_vars:
                    if env_var.startswith("NEO4J_AUTH="):
                        # Format is usually neo4j/password
                        auth = env_var.split("=", 1)[1]
                        if "/" in auth:
                            _, password = auth.split("/", 1)
                            return password
                            
        except Exception as e:
            logger.warning(f"Failed to inspect container {container_name}: {e}")
            
        return None
    
    def _try_localhost_connection(self) -> bool:
        """Try localhost connection - security compliant version"""
        logger.info("Checking localhost Neo4j connection...")
        
        # Security Note: No longer trying hardcoded passwords for compliance.
        # Connection must use environment variables, .env file, or Docker container detection.
        logger.info("⚠️  For security compliance, hardcoded password attempts disabled.")
        logger.info("💡 Please use environment variables, .env file, or Docker container with NEO4J_AUTH.")
        
        return False
    
    def _test_connection(self, uri: str, user: str, password: str, silent: bool = False) -> bool:
        """Test a Neo4j connection"""
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            
            # Test with a simple query
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
                if test_value == 1:
                    # Connection successful - save credentials
                    self.uri = uri
                    self.user = user
                    self.password = password
                    self.driver = driver
                    
                    # Get additional info
                    result = session.run("MATCH (n) RETURN count(n) as count")
                    node_count = result.single()["count"]
                    self.connection_info["node_count"] = node_count
                    
                    return True
                    
        except (AuthError, ServiceUnavailable) as e:
            if not silent:
                logger.debug(f"Connection failed: {e}")
        except Exception as e:
            if not silent:
                logger.warning(f"Unexpected error: {e}")
                
        return False
    
    def _provide_setup_instructions(self):
        """Provide clear setup instructions when connection fails"""
        logger.error("❌ Could not connect to Neo4j")
        
        print("\n" + "="*60)
        print("NEO4J SETUP INSTRUCTIONS")
        print("="*60)
        print("\nOption 1: Quick Docker Setup")
        print("-" * 30)
        print("docker run -d --name kgas-neo4j \\")
        print("  -p 7474:7474 -p 7687:7687 \\")
        print("  -e NEO4J_AUTH=neo4j/kgas123 \\")
        print("  neo4j:5.12.0")
        print("\nThen add to .env:")
        print("NEO4J_URI=bolt://localhost:7687")
        print("NEO4J_USER=neo4j")
        print("NEO4J_PASSWORD=kgas123")
        
        print("\n\nOption 2: Use Existing Neo4j")
        print("-" * 30)
        print("1. Check http://localhost:7474")
        print("2. Note your credentials")
        print("3. Update .env with correct values")
        
        print("\n\nOption 3: Environment Variables")
        print("-" * 30)
        print("export NEO4J_URI=bolt://localhost:7687")
        print("export NEO4J_USER=neo4j")
        print("export NEO4J_PASSWORD=your_password")
        print("="*60 + "\n")
    
    def create_kgas_indexes(self) -> bool:
        """Create indexes needed for KGAS"""
        if not self.driver:
            return False
            
        try:
            with self.driver.session() as session:
                # Create indexes
                indexes = [
                    "CREATE INDEX entity_id IF NOT EXISTS FOR (n:Entity) ON (n.entity_id)",
                    "CREATE INDEX entity_name IF NOT EXISTS FOR (n:Entity) ON (n.canonical_name)",
                    "CREATE INDEX mention_id IF NOT EXISTS FOR (m:Mention) ON (m.mention_id)",
                    "CREATE INDEX doc_id IF NOT EXISTS FOR (d:Document) ON (d.document_id)"
                ]
                
                for index in indexes:
                    try:
                        session.run(index)
                    except Exception as e:
                        logger.debug(f"Index creation note: {e}")
                        
                logger.info("✅ KGAS indexes created/verified")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            return False
    
    def get_connection_string(self) -> str:
        """Get formatted connection string for logging"""
        if self.uri and self.user:
            return f"{self.uri} (user: {self.user})"
        return "Not connected"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "connected": self.driver is not None,
            "uri": self.uri,
            "user": self.user,
            "source": self.connection_info.get("source", "none"),
            "node_count": self.connection_info.get("node_count", 0),
            "container": self.connection_info.get("container")
        }
    
    def close(self):
        """Close the driver connection"""
        if self.driver:
            self.driver.close()
            self.driver = None


# Global singleton instance
_neo4j_config = None


def get_neo4j_config() -> Neo4jConfig:
    """Get or create the global Neo4j configuration"""
    global _neo4j_config
    
    if _neo4j_config is None:
        _neo4j_config = Neo4jConfig()
        if _neo4j_config.connect():
            _neo4j_config.create_kgas_indexes()
            
            # Update environment for other components
            if _neo4j_config.uri:
                os.environ["NEO4J_URI"] = _neo4j_config.uri
                os.environ["NEO4J_USER"] = _neo4j_config.user
                os.environ["NEO4J_PASSWORD"] = _neo4j_config.password
                
    return _neo4j_config


def ensure_neo4j_connection() -> bool:
    """Ensure Neo4j is connected, return True if successful"""
    config = get_neo4j_config()
    return config.driver is not None