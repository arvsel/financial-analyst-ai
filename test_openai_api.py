"""
Test OpenAI API connection
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

print("Testing OpenAI API...")
print("="*60)

# Test embeddings (what we'll use for RAG)
try:
    response = client.embeddings.create(
        input="This is a test sentence",
        model="text-embedding-3-small"
    )
    
    embedding = response.data[0].embedding
    
    print("✓ OpenAI API is working!")
    print(f"\nCreated embedding with {len(embedding)} dimensions")
    print(f"First 10 values: {embedding[:10]}")
    
except Exception as e:
    print(f"✗ Error: {e}")

print("="*60)