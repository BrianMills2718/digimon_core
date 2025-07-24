#!/usr/bin/env python3
"""
Test file for MCP integration with gemini-review-tool
"""

def hello_world():
    """Simple function to test MCP integration"""
    return "Hello from MCP test!"

def calculate_sum(a, b):
    """Calculate sum of two numbers"""
    return a + b

if __name__ == "__main__":
    print(hello_world())
    print(f"Sum of 5 and 3: {calculate_sum(5, 3)}")