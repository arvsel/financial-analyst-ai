"""
Enhanced RAG system with section filtering
"""

import os
from pinecone import Pinecone
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

INDEX_NAME = "financial-docs"

def search_with_filter(query, section=None, ticker=None, top_k=5):
    """
    Search with optional filters by section and/or ticker
    """
    index = pc.Index(INDEX_NAME)
    
    # Create query embedding
    response = openai_client.embeddings.create(
        input=query,
        model="text-embedding-3-small",
        dimensions=768
    )
    query_embedding = response.data[0].embedding
    
    # Build filter
    filter_dict = {}
    if section:
        filter_dict['section'] = section
    if ticker:
        filter_dict['ticker'] = ticker
    
    # Search with filter
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict if filter_dict else None
    )
    
    # Extract documents
    documents = []
    for match in results['matches']:
        documents.append({
            'text': match['metadata']['text'],
            'score': match['score'],
            'section': match['metadata'].get('section', 'unknown'),
            'ticker': match['metadata'].get('ticker', 'unknown'),
            'id': match['id']
        })
    
    return documents

def ask_question(question, section=None, ticker=None):
    """
    RAG with optional section/ticker filtering
    """
    print(f"\n{'='*70}")
    print(f"Question: {question}")
    if section:
        print(f"Filtering by section: {section}")
    if ticker:
        print(f"Filtering by company: {ticker}")
    print('='*70)
    
    print("\nStep 1: 🔍 Searching Pinecone...")
    
    # Search with filters
    docs = search_with_filter(query=question, section=section, ticker=ticker, top_k=5)
    
    print(f"✓ Found {len(docs)} relevant chunks")
    
    # Build context
    context = "\n\n".join([
        f"[Source {i+1} - {doc['ticker']} - {doc['section']}]\n{doc['text']}"
        for i, doc in enumerate(docs)
    ])
    
    print("\nStep 2: 🤖 Generating answer with Claude...")
    
    # Create prompt
    prompt = f"""Based on the following excerpts from SEC 10-K filings, please answer the question.

Context from filings:
{context}

Question: {question}

Please provide a clear, detailed answer based on the documents above. Cite which companies and sections you're referencing.

Answer:"""
    
    # Get answer from Claude
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    answer = message.content[0].text
    
    # Display results
    print("\n" + "="*70)
    print("💡 ANSWER:")
    print("="*70)
    print(answer)
    
    print("\n" + "="*70)
    print("📚 SOURCES:")
    print("="*70)
    for i, doc in enumerate(docs, 1):
        print(f"\n[{i}] {doc['ticker']} - {doc['section'].upper().replace('_', ' ')}")
        print(f"    Relevance: {doc['score']:.3f}")
        print(f"    {doc['text'][:200]}...")
    
    return answer, docs

# Example queries
if __name__ == "__main__":
    # Test different filtering options
    
    print("\n" + "="*70)
    print("ENHANCED RAG SYSTEM - SECTION FILTERING DEMO")
    print("="*70)
    
    # Example 1: No filter (search all)
    print("\n\n" + "🔹"*35)
    print("EXAMPLE 1: General question (no filter)")
    print("🔹"*35)
    ask_question("What are the main revenue sources?")
    
    input("\n\nPress Enter for next example...")
    
    # Example 2: Filter by section
    print("\n\n" + "🔹"*35)
    print("EXAMPLE 2: Search only RISK FACTORS")
    print("🔹"*35)
    ask_question("What are the main risks?", section="risk_factors")
    
    input("\n\nPress Enter for next example...")
    
    # Example 3: Filter by company
    print("\n\n" + "🔹"*35)
    print("EXAMPLE 3: Microsoft only")
    print("🔹"*35)
    ask_question("What is the business model?", ticker="MSFT")
    
    input("\n\nPress Enter for next example...")
    
    # Example 4: Both filters
    print("\n\n" + "🔹"*35)
    print("EXAMPLE 4: Apple's business section")
    print("🔹"*35)
    ask_question("What products does the company sell?", section="business", ticker="AAPL")
    
    # Interactive mode
    print("\n\n" + "="*70)
    print("INTERACTIVE MODE")
    print("="*70)
    print("Ask questions with optional filters:")
    print("  - Type your question normally")
    print("  - Add 'section:risk_factors' to filter by section")
    print("  - Add 'ticker:MSFT' to filter by company")
    print("  - Type 'quit' to exit\n")
    
    while True:
        user_input = input("Your question: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Parse filters from input
        section_filter = None
        ticker_filter = None
        
        if 'section:' in user_input.lower():
            import re
            match = re.search(r'section:(\w+)', user_input, re.IGNORECASE)
            if match:
                section_filter = match.group(1).lower()
                user_input = re.sub(r'section:\w+', '', user_input, flags=re.IGNORECASE).strip()
        
        if 'ticker:' in user_input.lower():
            import re
            match = re.search(r'ticker:(\w+)', user_input, re.IGNORECASE)
            if match:
                ticker_filter = match.group(1).upper()
                user_input = re.sub(r'ticker:\w+', '', user_input, flags=re.IGNORECASE).strip()
        
        ask_question(user_input, section=section_filter, ticker=ticker_filter)
        print("\n" + "-"*70 + "\n")