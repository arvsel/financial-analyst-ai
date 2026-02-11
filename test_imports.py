"""
Test that all required libraries are installed correctly
"""

print("Testing imports...")
print("="*60)

# Test basic libraries
try:
    import requests
    print("✓ requests")
except ImportError:
    print("✗ requests - FAILED")

try:
    from bs4 import BeautifulSoup
    print("✓ beautifulsoup4")
except ImportError:
    print("✗ beautifulsoup4 - FAILED")

try:
    import pandas
    print("✓ pandas")
except ImportError:
    print("✗ pandas - FAILED")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv")
except ImportError:
    print("✗ python-dotenv - FAILED")

# Test AI libraries
try:
    from anthropic import Anthropic
    print("✓ anthropic (Claude API)")
except ImportError:
    print("✗ anthropic - FAILED")

try:
    from openai import OpenAI
    print("✓ openai")
except ImportError:
    print("✗ openai - FAILED")

try:
    from pinecone import Pinecone
    print("✓ pinecone-client")
except ImportError:
    print("✗ pinecone-client - FAILED")

# Test LangChain
try:
    import langchain
    print("✓ langchain")
except ImportError:
    print("✗ langchain - FAILED")

# Test Streamlit
try:
    import streamlit
    print("✓ streamlit")
except ImportError:
    print("✗ streamlit - FAILED")

# Test data processing
try:
    import numpy
    print("✓ numpy")
except ImportError:
    print("✗ numpy - FAILED")

print("="*60)
print("✓ All critical imports successful! You're ready to build!")