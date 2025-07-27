#!/usr/bin/env python3
"""
Automated Neo4j Setup for KGAS
Handles Neo4j startup, cleanup, and data preservation automatically
"""

import subprocess
import time
import socket
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AutomaticNeo4jManager:
    """Automatically manages Neo4j with data preservation"""
    
    def __init__(self, 
                 container_name: str = "neo4j-graphrag",
                 bolt_port: int = 7687,
                 http_port: int = 7474,
                 password: str = "testpassword"):
        self.container_name = container_name
        self.bolt_port = bolt_port
        self.http_port = http_port
        self.password = password
        self.neo4j_uri = f"bolt://localhost:{bolt_port}"
        
    def is_docker_available(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_port_open(self, host: str = "localhost", port: int = None) -> bool:
        """Check if Neo4j port is open"""
        port = port or self.bolt_port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                return sock.connect_ex((host, port)) == 0
        except Exception:
            return False
    
    def is_container_running(self) -> bool:
        """Check if Neo4j container is running"""
        try:
            result = subprocess.run([
                'docker', 'ps', '--filter', f'name={self.container_name}', 
                '--format', '{{.Names}}'
            ], capture_output=True, text=True, timeout=10)
            
            return self.container_name in result.stdout
        except Exception:
            return False
    
    def container_exists(self) -> bool:
        """Check if Neo4j container exists (stopped or running)"""
        try:
            result = subprocess.run([
                'docker', 'ps', '-a', '--filter', f'name={self.container_name}', 
                '--format', '{{.Names}}'
            ], capture_output=True, text=True, timeout=10)
            
            return self.container_name in result.stdout
        except Exception:
            return False
    
    def start_existing_container(self) -> Dict[str, Any]:
        """Start existing stopped container"""
        try:
            print(f"🔄 Starting existing Neo4j container: {self.container_name}")
            result = subprocess.run([
                'docker', 'start', self.container_name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Wait for Neo4j to be ready
                return self.wait_for_neo4j_ready()
            else:
                return {
                    'success': False,
                    'error': f'Failed to start container: {result.stderr}'
                }
        except Exception as e:
            return {'success': False, 'error': f'Container start failed: {e}'}
    
    def create_new_container(self) -> Dict[str, Any]:
        """Create and start new Neo4j container with data persistence"""
        try:
            print(f"🆕 Creating new Neo4j container: {self.container_name}")
            print("   This will automatically download Neo4j if needed...")
            
            # Simple, reliable Docker command that works across environments
            docker_cmd = [
                'docker', 'run', '-d',
                '--name', self.container_name,
                '-p', f'{self.http_port}:{self.http_port}',
                '-p', f'{self.bolt_port}:{self.bolt_port}',
                '-e', f'NEO4J_AUTH=neo4j/{self.password}',
                '-v', f'{self.container_name}_data:/data',  # Persistent data volume
                'neo4j:5.15'  # Use specific stable version
            ]
            
            print("   Running: " + " ".join(docker_cmd))
            
            # Run with longer timeout for image download
            result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                print(f"✓ Container created successfully")
                print(f"  - Container ID: {result.stdout.strip()[:12]}...")
                print(f"  - Data volume: {self.container_name}_data")
                print("  - Starting Neo4j service...")
                return self.wait_for_neo4j_ready(max_wait=90)  # Longer wait for first startup
            else:
                # Try to get more specific error info
                error_msg = result.stderr.strip()
                if "port is already allocated" in error_msg:
                    return {
                        'success': False,
                        'error': f'Ports {self.http_port}/{self.bolt_port} already in use. Stop existing Neo4j container first.'
                    }
                elif "image not found" in error_msg.lower():
                    return {
                        'success': False,
                        'error': 'Neo4j Docker image not available. Check internet connection.'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Container creation failed: {error_msg}'
                    }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Container creation timed out. This may be due to slow internet or Docker issues.'
            }
        except Exception as e:
            return {'success': False, 'error': f'Container creation failed: {e}'}
    
    def wait_for_neo4j_ready(self, max_wait: int = 60) -> Dict[str, Any]:
        """Wait for Neo4j to be ready to accept connections"""
        print(f"⏳ Waiting for Neo4j to be ready (max {max_wait}s)...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.is_port_open():
                # Try to connect with Neo4j driver
                try:
                    from neo4j import GraphDatabase
                    driver = GraphDatabase.driver(
                        self.neo4j_uri,
                        auth=('neo4j', self.password),
                        connection_timeout=5
                    )
                    
                    with driver.session() as session:
                        result = session.run("RETURN 1 as test")
                        test_value = result.single()["test"]
                        if test_value == 1:
                            driver.close()
                            ready_time = time.time() - start_time
                            print(f"✓ Neo4j ready in {ready_time:.1f}s")
                            return {'success': True, 'ready_time': ready_time}
                    
                    driver.close()
                except Exception as e:
                    pass  # Continue waiting
            
            time.sleep(2)
        
        return {
            'success': False,
            'error': f'Neo4j not ready after {max_wait}s'
        }
    
    def ensure_neo4j_available(self) -> Dict[str, Any]:
        """Ensure Neo4j is available, starting automatically if needed"""
        
        # Check if Docker is available
        if not self.is_docker_available():
            return {
                'success': False,
                'error': 'Docker not available. Please install Docker to use Neo4j integration.'
            }
        
        # Check if already running
        if self.is_container_running() and self.is_port_open():
            print("✓ Neo4j already running and accessible")
            return {'success': True, 'status': 'already_running'}
        
        # If container exists but is stopped, start it
        if self.container_exists():
            return self.start_existing_container()
        
        # Create new container
        return self.create_new_container()
    
    def get_connection_info(self) -> Dict[str, str]:
        """Get Neo4j connection information"""
        return {
            'bolt_uri': self.neo4j_uri,
            'http_url': f'http://localhost:{self.http_port}',
            'username': 'neo4j',
            'password': self.password,
            'container': self.container_name
        }
    
    def cleanup_safely(self) -> Dict[str, Any]:
        """Clean up connections without deleting data"""
        try:
            # Close any Python connections (handled by calling code)
            # Container and data volumes are preserved
            
            print("🧹 Neo4j cleanup completed:")
            print("  ✓ Connections can be closed by calling code")
            print("  ✓ Container left running for future use")
            print("  ✓ Data volumes preserved")
            print(f"  ✓ Access: http://localhost:{self.http_port}")
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop_container(self, remove_data: bool = False) -> Dict[str, Any]:
        """Stop container (optionally remove data - BE CAREFUL!)"""
        try:
            if not self.is_container_running():
                return {'success': True, 'message': 'Container not running'}
            
            print(f"🛑 Stopping Neo4j container: {self.container_name}")
            result = subprocess.run([
                'docker', 'stop', self.container_name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                message = f"Container {self.container_name} stopped"
                
                if remove_data:
                    print("⚠️  REMOVING CONTAINER AND DATA - THIS IS PERMANENT!")
                    subprocess.run(['docker', 'rm', self.container_name], timeout=30)
                    subprocess.run(['docker', 'volume', 'rm', f'{self.container_name}_data'], timeout=30)
                    subprocess.run(['docker', 'volume', 'rm', f'{self.container_name}_logs'], timeout=30)
                    message += " and data permanently deleted"
                else:
                    message += " - data preserved in volumes"
                
                return {'success': True, 'message': message}
            else:
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

def main():
    """Test the automatic Neo4j setup"""
    manager = AutomaticNeo4jManager()
    
    print("🚀 Testing Automatic Neo4j Setup")
    print("=" * 50)
    
    result = manager.ensure_neo4j_available()
    
    if result['success']:
        info = manager.get_connection_info()
        print("\n✅ Neo4j Setup Successful!")
        print(f"Bolt URI: {info['bolt_uri']}")
        print(f"Web UI: {info['http_url']}")
        print(f"Auth: {info['username']}/{info['password']}")
    else:
        print(f"\n❌ Neo4j Setup Failed: {result['error']}")

if __name__ == "__main__":
    main()