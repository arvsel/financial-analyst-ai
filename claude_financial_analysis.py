"""
Use Claude to analyze real SEC filing data
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load API keys
load_dotenv()

# Initialize Claude
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def ask_claude_about_filing(filing_text, question):
    """
    Send Claude a section of an SEC filing and ask a question
    """
    prompt = f"""Based on the following excerpt from an SEC filing, please answer this question:

Question: {question}

SEC Filing Excerpt:
{filing_text}

Please provide a clear, detailed answer based only on the information provided above."""

    print(f"Analyzing SEC filing...")
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response = message.content[0].text
    return response

# Read one of the SEC filings we downloaded earlier
try:
    with open("MSFT_filing.xml", "r") as f:
        filing_data = f.read()
    
    # Take just a portion (first 3000 characters)
    filing_excerpt = filing_data[:3000]
    
    # Ask Claude about it
    question = "What company is this filing for and what type of document is it?"
    
    print("="*60)
    print(f"QUESTION: {question}")
    print("="*60)
    
    answer = ask_claude_about_filing(filing_excerpt, question)
    
    print("\nCLAUDE'S RESPONSE:")
    print("="*60)
    print(answer)
    print("="*60)
    
    # Save
    with open("filing_analysis.txt", "w") as f:
        f.write(f"Question: {question}\n\n")
        f.write(f"Filing Excerpt:\n{filing_excerpt}\n\n")
        f.write(f"Answer: {answer}\n")
    
    print("\n✓ Analysis saved to filing_analysis.txt")
    
except FileNotFoundError:
    print("✗ MSFT_filing.xml not found!")
    print("Run fetch_sec_filing.py first to download SEC filings.")