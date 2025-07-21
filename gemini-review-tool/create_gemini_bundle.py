#!/usr/bin/env python3
"""
Create a manual bundle for Gemini validation
"""

def create_bundle():
    """Create XML bundle for Gemini validation"""
    
    # Read the async API client file
    with open('src/core/async_api_client.py', 'r') as f:
        content = f.read()
    
    # Create XML bundle
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<bundle>
    <project_name>Task 4 Async API Client Enhancement Validation</project_name>
    <files>
        <file>
            <path>src/core/async_api_client.py</path>
            <content><![CDATA[{content}]]></content>
        </file>
    </files>
</bundle>"""
    
    # Write bundle
    with open('async_api_client_bundle.xml', 'w') as f:
        f.write(xml_content)
    
    print("✅ Bundle created: async_api_client_bundle.xml")
    print(f"📊 Content length: {len(content)} characters")

if __name__ == "__main__":
    create_bundle()