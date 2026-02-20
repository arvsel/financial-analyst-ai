"""
Load 10-K sections into Pinecone with metadata
"""

import os
from parse_10k_sections import fetch_and_parse_10k_sections
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
INDEX_NAME = "financial-docs"

def upload_chunks_with_metadata(chunks):
    """
    Upload chunks to Pinecone with section metadata
    """
    index = pc.Index(INDEX_NAME)
    
    print(f"\nUploading {len(chunks)} chunks to Pinecone...")
    
    vectors = []
    batch_size = 100
    skipped = 0
    
    for i, chunk_data in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...", end='\r')
        
        # Create embedding with error handling
        try:
            response = openai_client.embeddings.create(
                input=chunk_data['text'],
                model="text-embedding-3-small",
                dimensions=768
            )
            embedding = response.data[0].embedding
        except Exception as e:
            skipped += 1
            continue
        
        # Prepare vector with rich metadata
        vector = (
            f"{chunk_data['ticker']}_{chunk_data['section']}_{chunk_data['chunk_id']}",
            embedding,
            {
                'text': chunk_data['text'],
                'ticker': chunk_data['ticker'],
                'section': chunk_data['section'],
                'chunk_id': chunk_data['chunk_id'],
                'doc_type': '10-K'
            }
        )
        vectors.append(vector)
        
        # Upload in batches
        if len(vectors) >= batch_size:
            index.upsert(vectors=vectors)
            vectors = []
        
        time.sleep(0.05)
    
    # Upload remaining
    if vectors:
        index.upsert(vectors=vectors)
    
    print(f"\n✓ Uploaded {len(chunks) - skipped} chunks (skipped {skipped})")

def load_company_with_sections(ticker):
    """
    Complete pipeline with section extraction
    """
    # Parse sections
    chunks = fetch_and_parse_10k_sections(ticker)
    
    if not chunks:
        print(f"✗ Failed to process {ticker}")
        return
    
    # Upload with metadata
    upload_chunks_with_metadata(chunks)

# Main
if __name__ == "__main__":
    print("="*60)
    print("LOADING 10-K SECTIONS INTO PINECONE")
    print("="*60)
    
    response = input("\nReplace existing data with section-labeled data? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        exit()
    
    # Clear existing data
    print("\nClearing existing data...")
    index = pc.Index(INDEX_NAME)
    index.delete(delete_all=True)
    time.sleep(2)
    print("✓ Cleared")
    
    # Load companies
    tickers = ['MSFT', 'AAPL']
    
    for ticker in tickers:
        try:
            load_company_with_sections(ticker)
        except Exception as e:
            print(f"\n✗ Error processing {ticker}: {e}")
        
        time.sleep(1)
    
    # Show stats
    time.sleep(2)
    stats = index.describe_index_stats()
    print(f"\n{'='*60}")
    print("FINAL STATS")
    print('='*60)
    print(f"Total vectors: {stats['total_vector_count']}")
    print("\n✓ Section-labeled data loaded!")