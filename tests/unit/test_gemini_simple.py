#!/usr/bin/env python3
"""
Simple test of Gemini 2.5 Flash API
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create model
model = genai.GenerativeModel('gemini-2.5-flash')

# Test simple generation
response = model.generate_content("What is 2+2?")
print(f"Response: {response.text}")

print("\nGemini 2.5 Flash is working!")