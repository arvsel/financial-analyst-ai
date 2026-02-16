"""
Test Claude API connection
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

print("Testing Claude API...")
print("="*60)

# Make a simple request
try:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello! Please respond with 'API connection successful!' if you can read this."}
        ]
    )
    
    # Extract response
    response = message.content[0].text
    
    print("✓ Claude API is working!")
    print(f"\nClaude's response: {response}")
    
except Exception as e:
    print(f"✗ Error: {e}")

print("="*60)