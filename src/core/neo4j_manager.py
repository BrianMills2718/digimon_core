#!/usr/bin/env python3
"""
Neo4j Manager - Automated Docker-based Neo4j Management

Automatically starts Neo4j when needed and provides connection validation.
Prevents infrastructure blockers in testing and development.
"""

import subprocess
import time
import socket
from typing import Optional, Dict, Any
import logging

from .config import ConfigurationManager

logger = logging.getLogger(__name__)


class Neo4jDockerManager:
    """Manages Neo4j Docker container lifecycle automatically"""
    
    def __init__(self, 
                 container_name: str = "neo4j-graphrag"):
        self.container_name = container_name
        
        # Get configuration from ConfigurationManager
        config_manager = ConfigurationManager()
        config = config_manager.get_config()
        
        # Extract host and port from URI
        uri_parts = config.neo4j.uri.replace("bolt://", "").split(":")
        self.host = uri_parts[0]
        self.port = int(uri_parts[1]) if len(uri_parts) > 1 else 7687
        
        self.username = config.neo4j.user
        self.password = config.neo4j.password
        self.bolt_uri = config.neo4j.uri
        
    def is_port_open(self, timeout: int = 1) -> bool:
        """Check if Neo4j port is accessible"""
        try:
            with socket.create_connection((self.host, self.port), timeout=timeout):
                return True
        except (socket.timeout, socket.error):
            return False
    
    def is_container_running(self) -> bool:
        """Check if Neo4j container is already running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}", "--filter", f"name={self.container_name}"],
                capture_output=True, text=True, timeout=10
            )
            return self.container_name in result.stdout
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def start_neo4j_container(self) -> Dict[str, Any]:
        """Start Neo4j container if not already running"""
        status = {
            "action": "none",
            "success": False,
            "message": "",
            "container_id": None
        }
        
        try:
            # Check if already running
            if self.is_container_running():
                if self.is_port_open():
                    status.update({
                        "action": "already_running",
                        "success": True,
                        "message": f"Neo4j container '{self.container_name}' already running"
                    })
                    return status
                else:
                    # Container running but port not accessible - restart it
                    self.stop_neo4j_container()
            
            # Remove any existing stopped container with same name
            subprocess.run(
                ["docker", "rm", "-f", self.container_name],
                capture_output=True, timeout=10
            )
            
            # Start new container
            cmd = [
                "docker", "run", "-d",
                "--name", self.container_name,
                "-p", f"{self.port}:7687",
                "-p", "7474:7474",
                "-e", f"NEO4J_AUTH={self.username}/{self.password}",
                "neo4j:latest"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                status.update({
                    "action": "started",
                    "success": True,
                    "message": f"Started Neo4j container: {container_id[:12]}",
                    "container_id": container_id
                })
                
                # Wait for Neo4j to be ready
                self._wait_for_neo4j_ready()
                
            else:
                status.update({
                    "action": "start_failed",
                    "success": False,
                    "message": f"Failed to start container: {result.stderr}"
                })
                
        except subprocess.TimeoutExpired:
            status.update({
                "action": "timeout",
                "success": False,
                "message": "Timeout starting Neo4j container"
            })
        except FileNotFoundError:
            status.update({
                "action": "docker_not_found",
                "success": False,
                "message": "Docker not available - cannot auto-start Neo4j"
            })
        except Exception as e:
            status.update({
                "action": "error",
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            })
        
        return status
    
    def stop_neo4j_container(self) -> bool:
        """Stop Neo4j container"""
        try:
            subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True, timeout=30
            )
            return True
        except:
            return False
    
    def _wait_for_neo4j_ready(self, max_wait: int = 30) -> bool:
        """Wait for Neo4j to be ready to accept connections"""
        print(f"⏳ Waiting for Neo4j to be ready on {self.bolt_uri}...")
        
        for i in range(max_wait):
            if self.is_port_open(timeout=2):
                # Port is open, now test actual Neo4j connection
                try:
                    from neo4j import GraphDatabase
                    driver = GraphDatabase.driver(
                        self.bolt_uri, 
                        auth=(self.username, self.password)
                    )
                    with driver.session() as session:
                        session.run("RETURN 1")
                    driver.close()
                    print(f"✅ Neo4j ready after {i+1} seconds")
                    return True
                except:
                    pass
            
            time.sleep(1)
            if i % 5 == 4:  # Every 5 seconds
                print(f"   Still waiting... ({i+1}/{max_wait}s)")
        
        print(f"❌ Neo4j not ready after {max_wait} seconds")
        return False
    
    def ensure_neo4j_available(self) -> Dict[str, Any]:
        """Ensure Neo4j is running and accessible, start if needed"""
        
        # Quick check if already available
        if self.is_port_open():
            return {
                "status": "available",
                "message": "Neo4j already accessible",
                "action": "none"
            }
        
        print("🔧 Neo4j not accessible - attempting auto-start...")
        start_result = self.start_neo4j_container()
        
        if start_result["success"]:
            return {
                "status": "started",
                "message": f"Neo4j auto-started: {start_result['message']}",
                "action": start_result["action"],
                "container_id": start_result.get("container_id")
            }
        else:
            return {
                "status": "failed",
                "message": f"Could not start Neo4j: {start_result['message']}",
                "action": start_result["action"]
            }


def ensure_neo4j_for_testing() -> bool:
    """
    Convenience function for tests - ensures Neo4j is available
    Returns True if Neo4j is accessible, False otherwise
    """
    manager = Neo4jDockerManager()
    result = manager.ensure_neo4j_available()
    
    if result["status"] in ["available", "started"]:
        print(f"✅ {result['message']}")
        return True
    else:
        print(f"❌ {result['message']}")
        return False


if __name__ == "__main__":
    # Test the manager
    print("Testing Neo4j Docker Manager...")
    manager = Neo4jDockerManager()
    result = manager.ensure_neo4j_available()
    print(f"Result: {result}")