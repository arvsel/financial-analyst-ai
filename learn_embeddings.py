"""
Learn how embeddings work - the foundation of semantic search
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_embedding(text):
    """
    Convert text into a vector of numbers (embedding)
    """
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
        dimensions=768
    )
    
    # The embedding is a list of 1536 numbers
    embedding = response.data[0].embedding
    return embedding

def cosine_similarity(vec1, vec2):
    """
    Measure how similar two embeddings are (0 to 1)
    1 = identical, 0 = completely different
    """
    dot_product = np.dot(vec1, vec2)
    magnitude = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return dot_product / magnitude

# Test with financial terms
texts = [
    "Microsoft's cloud revenue grew 25% year-over-year",
    "Azure sales increased significantly in the last quarter",
    "The company sells pizza in New York",
    "Revenue from cloud services showed strong growth",
    "Apple released a new iPhone model",
]

print("Creating embeddings for sample texts...")
print("="*60)

embeddings = []
for i, text in enumerate(texts, 1):
    emb = get_embedding(text)
    embeddings.append(emb)
    print(f"{i}. Created embedding for: '{text}'")
    print(f"   Vector size: {len(emb)} dimensions")
    print(f"   First 5 values: {emb[:5]}")
    print()

print("\n" + "="*60)
print("SIMILARITY SCORES (how related are these sentences?)")
print("="*60 + "\n")

# Compare first text to all others
query_text = texts[0]
query_embedding = embeddings[0]

print(f"Comparing everything to: '{query_text}'\n")

for i, (text, embedding) in enumerate(zip(texts[1:], embeddings[1:]), 1):
    similarity = cosine_similarity(query_embedding, embedding)
    
    # Visual representation
    bar_length = int(similarity * 50)
    bar = "█" * bar_length
    
    print(f"Text {i}: {text}")
    print(f"Similarity: {similarity:.3f} {bar}")
    print()

print("="*60)
print("KEY INSIGHT:")
print("="*60)
print("Notice: Sentences about cloud growth are very similar (>0.80)")
print("But sentences about pizza and iPhones are different (<0.50)")
print("\nThis is how semantic search works! 🎯")