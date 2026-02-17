"""
Test Pinecone connection
"""

import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

print("Testing Pinecone connection...")
print("="*60)

try:
    # List all indexes
    indexes = pc.list_indexes()
    
    print("✓ Connected to Pinecone!")
    print(f"\nFound {len(indexes)} index(es):")
    
    for index in indexes:
        print(f"  - {index.name}")
        print(f"    Dimension: {index.dimension}")
        print(f"    Metric: {index.metric}")
        print(f"    Status: {index.status.state}")
    
    # Connect to your index
    index = pc.Index("financial-docs")
    
    # Get stats
    stats = index.describe_index_stats()
    print(f"\nIndex 'financial-docs' stats:")
    print(f"  Total vectors: {stats['total_vector_count']}")
    print(f"  Dimension: {stats['dimension']}")
    
    print("\n✓ Pinecone is ready to use!")
    
except Exception as e:
    print(f"✗ Error: {e}")

print("="*60)