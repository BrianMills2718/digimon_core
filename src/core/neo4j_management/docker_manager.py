"""
Docker Manager

Handles Neo4j Docker container lifecycle management, startup, and monitoring.
"""

import subprocess
import socket
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .neo4j_types import (
    Neo4jConfig, ContainerStatus, ContainerInfo, 
    ContainerError
)

logger = logging.getLogger(__name__)


class DockerManager:
    """Manages Neo4j Docker container lifecycle and monitoring."""
    
    def __init__(self, config: Neo4jConfig):
        self.config = config
        self._container_info = ContainerInfo(status=ContainerStatus.NOT_FOUND)
    
    def is_port_open(self, timeout: int = 1) -> bool:
        """Check if Neo4j port is accessible."""
        try:
            with socket.create_connection((self.config.host, self.config.port), timeout=timeout):
                return True
        except (socket.timeout, socket.error):
            return False
    
    def is_container_running(self) -> bool:
        """Check if Neo4j container is already running."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}", "--filter", f"name={self.config.container_name}"],
                capture_output=True, text=True, timeout=10
            )
            
            is_running = self.config.container_name in result.stdout
            
            if is_running:
                self._update_container_info_from_docker()
            else:
                self._container_info.status = ContainerStatus.STOPPED
            
            return is_running
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Failed to check container status: {e}")
            self._container_info.status = ContainerStatus.ERROR
            self._container_info.error_message = str(e)
            return False
    
    def _update_container_info_from_docker(self) -> None:
        """Update container info from Docker inspect."""
        try:
            result = subprocess.run(
                ["docker", "inspect", self.config.container_name, "--format", 
                 "{{.Id}}|{{.Created}}|{{.State.Status}}"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                if len(parts) >= 3:
                    container_id, created_str, status = parts
                    
                    try:
                        created_at = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    except ValueError:
                        created_at = None
                    
                    self._container_info = ContainerInfo(
                        status=ContainerStatus.RUNNING if status == 'running' else ContainerStatus.STOPPED,
                        container_id=container_id,
                        created_at=created_at,
                        port_mapping={
                            "bolt": self.config.port,
                            "http": 7474
                        }
                    )
                    
        except Exception as e:
            logger.warning(f"Failed to update container info: {e}")
    
    def start_neo4j_container(self) -> Dict[str, Any]:
        """Start Neo4j container if not already running."""
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
                        "message": f"Neo4j container '{self.config.container_name}' already running"
                    })
                    return status
                else:
                    # Container running but port not accessible - restart it
                    logger.warning("Container running but port not accessible, restarting")
                    self.stop_neo4j_container()
            
            # Remove any existing stopped container with same name
            subprocess.run(
                ["docker", "rm", "-f", self.config.container_name],
                capture_output=True, timeout=10
            )
            
            # Start new container
            cmd = [
                "docker", "run", "-d",
                "--name", self.config.container_name,
                "-p", f"{self.config.port}:7687",
                "-p", "7474:7474",
                "-e", f"NEO4J_AUTH={self.config.username}/{self.config.password}",
                "neo4j:latest"
            ]
            
            logger.info(f"Starting Neo4j container with command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                
                # Update container info
                self._container_info = ContainerInfo(
                    status=ContainerStatus.STARTING,
                    container_id=container_id,
                    created_at=datetime.now(),
                    port_mapping={
                        "bolt": self.config.port,
                        "http": 7474
                    }
                )
                
                status.update({
                    "action": "started",
                    "success": True,
                    "message": f"Started Neo4j container: {container_id[:12]}",
                    "container_id": container_id
                })
                
                # Wait for Neo4j to be ready
                if self._wait_for_neo4j_ready():
                    self._container_info.status = ContainerStatus.RUNNING
                    logger.info("Neo4j container started and ready")
                else:
                    status["success"] = False
                    status["message"] = "Container started but Neo4j not ready"
                    
            else:
                error_msg = result.stderr or "Unknown error"
                self._container_info.status = ContainerStatus.ERROR
                self._container_info.error_message = error_msg
                
                status.update({
                    "action": "start_failed",
                    "success": False,
                    "message": f"Failed to start container: {error_msg}"
                })
                
        except subprocess.TimeoutExpired:
            status.update({
                "action": "timeout",
                "success": False,
                "message": "Timeout starting Neo4j container"
            })
            self._container_info.status = ContainerStatus.ERROR
            self._container_info.error_message = "Startup timeout"
            
        except FileNotFoundError:
            status.update({
                "action": "docker_not_found",
                "success": False,
                "message": "Docker not available - cannot auto-start Neo4j"
            })
            self._container_info.status = ContainerStatus.ERROR
            self._container_info.error_message = "Docker not available"
            
        except Exception as e:
            error_msg = str(e)
            status.update({
                "action": "error",
                "success": False,
                "message": f"Unexpected error: {error_msg}"
            })
            self._container_info.status = ContainerStatus.ERROR
            self._container_info.error_message = error_msg
        
        return status
    
    def stop_neo4j_container(self) -> bool:
        """Stop Neo4j container."""
        try:
            result = subprocess.run(
                ["docker", "stop", self.config.container_name],
                capture_output=True, timeout=30
            )
            
            if result.returncode == 0:
                self._container_info.status = ContainerStatus.STOPPED
                logger.info(f"Successfully stopped Neo4j container: {self.config.container_name}")
                return True
            else:
                error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                logger.error(f"Failed to stop container: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop Neo4j container: {e}")
            self._container_info.status = ContainerStatus.ERROR
            self._container_info.error_message = str(e)
            return False
    
    def _wait_for_neo4j_ready(self, max_wait: int = 30) -> bool:
        """Wait for Neo4j to be ready to accept connections."""
        logger.info(f"⏳ Waiting for Neo4j to be ready on {self.config.bolt_uri}...")
        
        for i in range(max_wait):
            if self.is_port_open(timeout=2):
                # Port is open, now test actual Neo4j connection
                try:
                    from neo4j import GraphDatabase
                    driver = GraphDatabase.driver(
                        self.config.bolt_uri, 
                        auth=(self.config.username, self.config.password)
                    )
                    with driver.session() as session:
                        session.run("RETURN 1")
                    driver.close()
                    
                    logger.info(f"✅ Neo4j ready after {i+1} seconds")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Neo4j connection attempt failed: {e}")
                    pass
            
            # Brief delay before next check
            time.sleep(1)
            if i % 5 == 4:  # Every 5 seconds
                logger.info(f"   Still waiting... ({i+1}/{max_wait}s)")
        
        logger.warning(f"❌ Neo4j not ready after {max_wait} seconds")
        return False
    
    def ensure_neo4j_available(self) -> Dict[str, Any]:
        """Ensure Neo4j is running and accessible, start if needed."""
        
        # Quick check if already available
        if self.is_port_open():
            return {
                "status": "available",
                "message": "Neo4j already accessible",
                "action": "none"
            }
        
        logger.info("🔧 Neo4j not accessible - attempting auto-start...")
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
    
    def get_container_info(self) -> ContainerInfo:
        """Get current container information."""
        # Update info if container is supposed to be running
        if self._container_info.status == ContainerStatus.RUNNING:
            self.is_container_running()  # This updates the info
        
        return self._container_info
    
    def get_container_logs(self, tail_lines: int = 50) -> str:
        """Get container logs for debugging."""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail_lines), self.config.container_name],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error getting logs: {result.stderr}"
                
        except Exception as e:
            return f"Failed to get container logs: {e}"
    
    def get_container_statistics(self) -> Dict[str, Any]:
        """Get comprehensive container statistics."""
        stats = {
            "container_name": self.config.container_name,
            "status": self._container_info.status.value,
            "container_id": self._container_info.container_id,
            "created_at": self._container_info.created_at.isoformat() if self._container_info.created_at else None,
            "port_accessible": self.is_port_open(),
            "port_mapping": self._container_info.port_mapping,
            "error_message": self._container_info.error_message
        }
        
        # Add Docker stats if container is running
        if self._container_info.status == ContainerStatus.RUNNING and self._container_info.container_id:
            try:
                result = subprocess.run(
                    ["docker", "stats", "--no-stream", "--format", 
                     "table {{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}}", 
                     self.config.container_name],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        data = lines[1].split(',')
                        if len(data) >= 4:
                            stats["resource_usage"] = {
                                "cpu_percent": data[0].strip(),
                                "memory_usage": data[1].strip(),
                                "network_io": data[2].strip(),
                                "block_io": data[3].strip()
                            }
                            
            except Exception as e:
                logger.debug(f"Failed to get container stats: {e}")
        
        return stats