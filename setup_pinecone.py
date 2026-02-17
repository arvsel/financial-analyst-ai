"""
Upload documents to Pinecone with embeddings
"""

import os
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

# Initialize clients
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Index name
INDEX_NAME = "financial-docs"

def add_documents_to_index(documents):
    """
    Add documents to Pinecone with embeddings
    """
    index = pc.Index(INDEX_NAME)
    
    print(f"Adding {len(documents)} documents to Pinecone...")
    print("="*60)
    
    vectors_to_upsert = []
    
    for i, doc in enumerate(documents):
        print(f"Processing document {i+1}/{len(documents)}...", end='\r')
        
        # Create embedding
        response = openai_client.embeddings.create(
            input=doc,
            model="text-embedding-3-small",
            dimensions=768
        )
        embedding = response.data[0].embedding
        
        # Prepare vector for Pinecone
        # Format: (id, embedding, metadata)
        vector = (
            f"doc_{i}",           # Unique ID
            embedding,            # The 1536-dimensional vector
            {"text": doc,         # Store original text as metadata
             "doc_id": i}
        )
        vectors_to_upsert.append(vector)
        
        time.sleep(0.05)  # Small delay to avoid rate limits
    
    # Upload to Pinecone in one batch
    index.upsert(vectors=vectors_to_upsert)
    
    print(f"\n✓ Successfully added {len(documents)} documents to Pinecone!")
    
    # Check index stats
    time.sleep(1)  # Wait for index to update
    stats = index.describe_index_stats()
    print(f"\nTotal vectors in index: {stats['total_vector_count']}")

# Sample financial documents (same as before)
sample_documents = [
    "Microsoft Corporation reported total revenue of $211.9 billion for fiscal year 2024, representing 16% growth year-over-year.",
    "Azure and cloud services revenue grew 31% in Q4 2024, driven by strong demand for AI capabilities.",
    "Intelligent Cloud segment revenue was $87.9 billion, up 20% from prior year.",
    "Operating income increased to $109.4 billion, with operating margin of 51.6%.",
    "Microsoft returned $21.7 billion to shareholders through share repurchases and dividends.",
    "Commercial products and cloud services revenue increased 16% to $176.9 billion.",
    "LinkedIn revenue surpassed $16 billion for the fiscal year, growing 10% year-over-year.",
    "Dynamics products and cloud services revenue grew 22%, with Dynamics 365 growing 25%.",
    "Gaming revenue increased 31% driven by the Activision acquisition.",
    "Microsoft Cloud gross margin percentage was 72%, up 2 points year-over-year.",
]

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PINECONE SETUP - Adding Sample Documents")
    print("="*60 + "\n")
    
    add_documents_to_index(sample_documents)
    
    print("\n" + "="*60)
    print("✓ Setup complete! Your vector database is ready!")
    print("="*60)