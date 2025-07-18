#!/usr/bin/env python3
"""Simple test to debug contract loading"""

from pathlib import Path

# Add src to path for imports

from core.contract_validator import ContractValidator

def main():
    print("=== Simple Contract Loading Test ===")
    
    # Create validator
    contracts_dir = Path(__file__).parent / "contracts"
    print(f"Contracts directory: {contracts_dir}")
    print(f"Contracts directory exists: {contracts_dir.exists()}")
    
    tools_dir = contracts_dir / "tools"
    print(f"Tools directory: {tools_dir}")
    print(f"Tools directory exists: {tools_dir.exists()}")
    
    # List files in tools directory
    if tools_dir.exists():
        print("Files in tools directory:")
        for file in tools_dir.glob("*.yaml"):
            print(f"  - {file.name}")
    
    try:
        validator = ContractValidator(str(contracts_dir))
        print("✓ Validator created successfully")
        
        # Try to load each contract file directly
        for contract_file in tools_dir.glob("*.yaml"):
            tool_id = contract_file.stem
            print(f"\nTrying to load tool_id: {tool_id}")
            
            try:
                contract = validator.load_contract(tool_id)
                print(f"✓ Loaded contract: {contract['tool_id']}")
            except Exception as e:
                print(f"✗ Failed to load {tool_id}: {e}")
                
                # Try loading the file directly
                try:
                    import yaml
                    with open(contract_file, 'r') as f:
                        direct_contract = yaml.safe_load(f)
                    print(f"  Direct load successful, tool_id in file: {direct_contract.get('tool_id')}")
                    
                    # Check if tool_id matches filename
                    if direct_contract.get('tool_id') == tool_id:
                        print("  Tool ID matches filename")
                    else:
                        print(f"  Tool ID mismatch: file={tool_id}, contract={direct_contract.get('tool_id')}")
                        
                except Exception as direct_e:
                    print(f"  Direct load also failed: {direct_e}")
        
    except Exception as e:
        print(f"✗ Failed to create validator: {e}")

if __name__ == "__main__":
    main()