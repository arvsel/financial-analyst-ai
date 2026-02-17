"""
RAG System: Retrieve relevant documents from Pinecone, then generate answers with Claude
"""

import os
from pinecone import Pinecone
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize all clients
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

INDEX_NAME = "financial-docs"

def search_similar_documents(query, top_k=5):
    """
    Find documents similar to the query
    """
    # Get index
    index = pc.Index(INDEX_NAME)
    
    # Create embedding for query
    response = openai_client.embeddings.create(
        input=query,
        model="text-embedding-3-small",
        dimensions=768
    )
    query_embedding = response.data[0].embedding
    
    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    # Extract documents
    documents = []
    for match in results['matches']:
        documents.append({
            'text': match['metadata']['text'],
            'score': match['score'],
            'id': match['id']
        })
    
    return documents

def ask_question_with_context(question):
    """
    RAG Pipeline:
    1. Retrieve relevant documents from Pinecone
    2. Augment prompt with context
    3. Generate answer with Claude
    """
    print(f"Question: {question}\n")
    print("Step 1: 🔍 Searching for relevant documents in Pinecone...")
    
    # Retrieve relevant documents
    relevant_docs = search_similar_documents(question, top_k=3)
    
    print(f"✓ Found {len(relevant_docs)} relevant documents\n")
    
    # Build context from documents
    context = "\n\n".join([
        f"[Document {i+1}] {doc['text']}"
        for i, doc in enumerate(relevant_docs)
    ])
    
    print("Step 2: 🤖 Generating answer with Claude...")
    
    # Create prompt for Claude
    prompt = f"""Based on the following financial documents, please answer the question.

Documents:
{context}

Question: {question}

Please provide a detailed answer based on the documents above. If the documents don't contain enough information to answer fully, say so.

Answer:"""
    
    # Get answer from Claude
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    answer = message.content[0].text
    
    # Print results
    print("\n" + "="*70)
    print("💡 ANSWER:")
    print("="*70)
    print(answer)
    print("\n" + "="*70)
    print("📚 SOURCE DOCUMENTS:")
    print("="*70)
    for i, doc in enumerate(relevant_docs, 1):
        print(f"\n[{i}] (similarity: {doc['score']:.3f})")
        print(doc['text'])
    
    return answer, relevant_docs

# Test it!
if __name__ == "__main__":
    questions = [
        "What was Microsoft's total revenue for fiscal year 2024?",
        "How did Azure perform in Q4?",
        "What were the key drivers of gaming revenue growth?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n\n{'='*70}")
        print(f"QUESTION {i}")
        print('='*70 + "\n")
        ask_question_with_context(question)
        
        if i < len(questions):
            input("\nPress Enter for next question...")

# Add after the existing test questions

print("\n" + "="*70)
print("INTERACTIVE RAG MODE")
print("="*70)
print("Ask questions about the SEC filings (or 'quit' to exit)\n")

while True:
    user_question = input("Your question: ")
    
    if user_question.lower() in ['quit', 'exit', 'q']:
        print("\n👋 Goodbye!")
        break
    
    if not user_question.strip():
        continue
    
    print()
    ask_question_with_context(user_question)
    print("\n" + "-"*70 + "\n")