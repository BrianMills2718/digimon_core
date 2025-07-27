#!/usr/bin/env python3
"""
One-Click KGAS Setup with Neo4j
Perfect for UI integration - handles everything automatically
"""

import sys
import time
from auto_neo4j_setup import AutomaticNeo4jManager

def one_click_setup(show_progress=True):
    """
    One-click setup for KGAS with Neo4j
    Returns: (success: bool, info: dict, error: str)
    """
    
    if show_progress:
        print("🚀 KGAS One-Click Setup Starting...")
        print("=" * 50)
    
    try:
        # Initialize Neo4j manager
        manager = AutomaticNeo4jManager(
            container_name="kgas-neo4j",
            password="testpassword"
        )
        
        if show_progress:
            print("🔍 Checking system requirements...")
        
        # Check Docker
        if not manager.is_docker_available():
            return False, {}, "Docker not available. Please install Docker Desktop."
        
        if show_progress:
            print("✓ Docker available")
            print("🔄 Setting up Neo4j database...")
        
        # Setup Neo4j automatically
        result = manager.ensure_neo4j_available()
        
        if result['success']:
            info = manager.get_connection_info()
            
            if show_progress:
                print("✅ KGAS Setup Complete!")
                print(f"  - Neo4j Web UI: {info['http_url']}")
                print(f"  - Database ready for KGAS")
                print(f"  - Data will persist across sessions")
                print("\n🎯 You can now run KGAS operations!")
            
            return True, info, ""
        else:
            error = result.get('error', 'Unknown error')
            if show_progress:
                print(f"❌ Setup failed: {error}")
            return False, {}, error
            
    except Exception as e:
        error = f"Setup error: {str(e)}"
        if show_progress:
            print(f"❌ {error}")
        return False, {}, error

def setup_status():
    """Check if KGAS setup is already running"""
    try:
        manager = AutomaticNeo4jManager()
        
        if manager.is_container_running() and manager.is_port_open():
            info = manager.get_connection_info()
            return {
                'status': 'running',
                'message': 'KGAS is ready to use',
                'web_ui': info['http_url'],
                'container': info['container']
            }
        elif manager.container_exists():
            return {
                'status': 'stopped',
                'message': 'KGAS container exists but is stopped',
                'action': 'Can be started automatically'
            }
        else:
            return {
                'status': 'not_setup',
                'message': 'KGAS not set up yet',
                'action': 'Run one-click setup'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Status check failed: {e}',
            'action': 'Check Docker installation'
        }

def stop_kgas(preserve_data=True):
    """Stop KGAS (optionally preserve data)"""
    try:
        manager = AutomaticNeo4jManager()
        result = manager.stop_container(remove_data=not preserve_data)
        
        if result['success']:
            return True, result['message']
        else:
            return False, result.get('error', 'Stop failed')
    except Exception as e:
        return False, f"Stop error: {e}"

# UI Integration Functions
def ui_setup_kgas():
    """UI-friendly setup function"""
    return one_click_setup(show_progress=False)

def ui_get_status():
    """UI-friendly status check"""
    return setup_status()

def ui_stop_kgas():
    """UI-friendly stop function"""
    return stop_kgas(preserve_data=True)

def main():
    """Command line interface"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'setup':
            success, info, error = one_click_setup()
            sys.exit(0 if success else 1)
            
        elif command == 'status':
            status = setup_status()
            print(f"Status: {status['status']}")
            print(f"Message: {status['message']}")
            if 'web_ui' in status:
                print(f"Web UI: {status['web_ui']}")
            sys.exit(0)
            
        elif command == 'stop':
            success, message = stop_kgas()
            print(message)
            sys.exit(0 if success else 1)
            
        else:
            print("Usage: python one_click_kgas_setup.py [setup|status|stop]")
            sys.exit(1)
    else:
        # Interactive mode
        print("🚀 KGAS One-Click Setup")
        print("1. Setup KGAS")
        print("2. Check Status") 
        print("3. Stop KGAS")
        choice = input("Choose (1-3): ").strip()
        
        if choice == '1':
            one_click_setup()
        elif choice == '2':
            status = setup_status()
            print(f"\nStatus: {status['status']}")
            print(f"Message: {status['message']}")
        elif choice == '3':
            success, message = stop_kgas()
            print(f"\n{message}")

if __name__ == "__main__":
    main()