"""
Load real SEC filings into Pinecone
"""

import os
from parse_10k_edgar import fetch_and_parse_10k
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
INDEX_NAME = "financial-docs"

def upload_chunks_to_pinecone(ticker, chunks):
    """
    Upload document chunks to Pinecone with embeddings
    """
    index = pc.Index(INDEX_NAME)
    
    print(f"\nUploading {len(chunks)} chunks to Pinecone...")
    
    vectors = []
    batch_size = 100  # Upload in batches
    
    for i, chunk in enumerate(chunks):  # ← This needs to be indented!
        print(f"Processing chunk {i+1}/{len(chunks)}...", end='\r')
        
        # Create embedding with error handling
        try:
            response = openai_client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small",
                dimensions=768
            )
            embedding = response.data[0].embedding
        except Exception as e:
            # Skip chunks that are too long
            print(f"\n⚠️  Skipping chunk {i+1} (too long)")
            continue
        
        # Prepare vector
        vector = (
            f"{ticker}_chunk_{i}",
            embedding,
            {
                'text': chunk,
                'ticker': ticker,
                'chunk_id': i,
                'doc_type': '10-K'
            }
        )
        vectors.append(vector)
        
        # Upload in batches
        if len(vectors) >= batch_size:
            index.upsert(vectors=vectors)
            vectors = []
        
        time.sleep(0.05)  # Rate limiting
    
    # Upload remaining vectors
    if vectors:
        index.upsert(vectors=vectors)
    
    print(f"\n✓ Uploaded chunks for {ticker}")

def load_company_filing(ticker):
    """
    Complete pipeline: fetch, parse, and upload to Pinecone
    """
    # Fetch and parse
    chunks = fetch_and_parse_10k(ticker)
    
    if not chunks:
        print(f"✗ Failed to process {ticker}")
        return
    
    # Upload to Pinecone
    upload_chunks_to_pinecone(ticker, chunks)

# Main execution
if __name__ == "__main__":
    # Clear existing data first (optional)
    print("="*60)
    print("LOADING REAL SEC FILINGS INTO PINECONE")
    print("="*60)
    
    response = input("\nThis will replace sample data with real filings. Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        exit()
    
    # Delete all existing vectors (start fresh)
    print("\nClearing existing data...")
    index = pc.Index(INDEX_NAME)
    index.delete(delete_all=True)
    time.sleep(2)  # Wait for deletion to complete
    print("✓ Cleared")
    
    # Load filings for multiple companies
    tickers = ['MSFT', 'AAPL']
    
    for ticker in tickers:
        try:
            load_company_filing(ticker)
        except Exception as e:
            print(f"\n✗ Error processing {ticker}: {e}")
        
        time.sleep(1)  # Be nice to SEC servers
    
    # Show final stats
    time.sleep(2)
    stats = index.describe_index_stats()
    print(f"\n{'='*60}")
    print("FINAL STATS")
    print('='*60)
    print(f"Total vectors in index: {stats['total_vector_count']}")
    print("\n✓ Real SEC filings loaded successfully!")