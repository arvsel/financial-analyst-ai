"""
Build a semantic search engine for financial documents
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Sample financial documents (later we'll use real SEC filings)
documents = [
    "Microsoft reported Q4 revenue of $62B, up 17% YoY. Cloud services were the primary driver.",
    "Azure revenue grew 29% in constant currency, driven by AI services adoption.",
    "Operating expenses increased 13% to $15.9B due to investments in AI infrastructure.",
    "The company returned $8.4B to shareholders through dividends and share repurchases.",
    "LinkedIn revenue increased 10% driven by Talent Solutions and Marketing Solutions.",
    "Gaming revenue declined 7% due to lower Xbox hardware sales.",
    "Gross margin improved to 69.8%, up from 68.5% last year.",
    "Free cash flow was $23.2B, up 18% year-over-year.",
    "Microsoft announced a strategic partnership with OpenAI for AI development.",
    "The company faces regulatory scrutiny over its acquisition of Activision Blizzard.",
]

def create_embedding(text):
    """Create embedding for a text"""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
        dimensions=768
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    """Calculate similarity between two vectors"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def search_documents(query, top_k=3):
    """
    Find the most relevant documents for a query
    """
    print(f"🔍 Searching for: '{query}'")
    print("="*60)
    
    # Create embedding for the query
    print("Creating query embedding...")
    query_embedding = create_embedding(query)
    
    # Calculate similarity with each document
    print("Comparing to all documents...")
    results = []
    for doc in documents:
        doc_embedding = create_embedding(doc)
        similarity = cosine_similarity(query_embedding, doc_embedding)
        results.append({
            'document': doc,
            'similarity': similarity
        })
    
    # Sort by similarity (highest first)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Return top K results
    print(f"\nTop {top_k} results:")
    print("="*60)
    return results[:top_k]

# Test different queries
queries = [
    "How is the cloud business performing?",
    "What about shareholder returns?",
    "Tell me about profitability and margins",
    "Any regulatory issues?",
]

for i, query in enumerate(queries, 1):
    print(f"\n\n{'='*60}")
    print(f"QUERY {i}")
    print('='*60)
    
    results = search_documents(query, top_k=3)
    
    for j, result in enumerate(results, 1):
        # Visual similarity bar
        bar_length = int(result['similarity'] * 50)
        bar = "█" * bar_length
        
        print(f"\n#{j} (Similarity: {result['similarity']:.3f}) {bar}")
        print(f"    {result['document']}")
    
    print("\n" + "="*60)

print("\n\n✅ Semantic search complete!")
print("\nKEY INSIGHT:")
print("Notice how it finds relevant documents even when they use different words!")
print("'cloud business' → finds 'Azure revenue'")
print("'shareholder returns' → finds 'dividends and share repurchases'")

print("\n" + "="*60)
print("INTERACTIVE SEARCH MODE")
print("="*60)
print("Enter your questions (or 'quit' to exit)\n")

while True:
    user_query = input("Your question: ")
    
    if user_query.lower() in ['quit', 'exit', 'q']:
        print("\n👋 Goodbye!")
        break
    
    if not user_query.strip():
        continue
    
    print()
    results = search_documents(user_query, top_k=3)
    
    for j, result in enumerate(results, 1):
        bar_length = int(result['similarity'] * 50)
        bar = "█" * bar_length
        
        print(f"\n#{j} (Similarity: {result['similarity']:.3f}) {bar}")
        print(f"    {result['document']}")
    
    print("\n" + "-"*60 + "\n")