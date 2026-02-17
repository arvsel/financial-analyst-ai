"""
Parse 10-K using sec-edgar-downloader library (most reliable method)
"""

from sec_edgar_downloader import Downloader
import os
import re
import shutil

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.split()) > 50:  # Only chunks with at least 50 words
            chunks.append(chunk)
    
    return chunks

def clean_text(content):
    """Clean SEC filing text - improved version"""
    import html
    
    # First decode HTML entities (&#160; → space, etc.)
    text = html.unescape(content)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    
    # Remove common SEC filing artifacts
    text = re.sub(r'\s+Table of Contents\s+', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+PART\s+[IVX]+\s+', ' ', text)
    
    return text.strip()

def fetch_and_parse_10k(ticker):
    """
    Download and parse latest 10-K
    """
    print(f"\n{'='*60}")
    print(f"Processing {ticker}")
    print('='*60)
    
    # Create downloader
    dl = Downloader("FinancialAnalystAI", "arvindselvakesari@example.com")
    
    # Download latest 10-K
    print("Step 1: Downloading latest 10-K from SEC...")
    try:
        dl.get("10-K", ticker, limit=1, download_details=True)
    except Exception as e:
        print(f"✗ Error downloading: {e}")
        return []
    
    # Find the downloaded file
    base_path = "sec-edgar-filings"
    ticker_path = os.path.join(base_path, ticker, "10-K")
    
    if not os.path.exists(ticker_path):
        print(f"✗ Filing folder not found")
        return []
    
    # Get the most recent filing folder
    filing_folders = [f for f in os.listdir(ticker_path) if os.path.isdir(os.path.join(ticker_path, f))]
    
    if not filing_folders:
        print("✗ No filings found")
        return []
    
    # Sort by date (folder names are dates)
    filing_folders.sort(reverse=True)
    latest_folder = filing_folders[0]
    
    file_path = os.path.join(ticker_path, latest_folder, "full-submission.txt")
    
    if not os.path.exists(file_path):
        print(f"✗ Submission file not found at {file_path}")
        return []
    
    print(f"✓ Found filing from {latest_folder}")
    
    # Read and clean
    print("Step 2: Extracting and cleaning text...")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    text = clean_text(content)
    print(f"✓ Extracted {len(text):,} characters")
    
    # Chunk
    print("Step 3: Creating chunks...")
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    print(f"✓ Created {len(chunks)} chunks")
    
    return chunks

# Test
if __name__ == "__main__":
    ticker = "MSFT"
    chunks = fetch_and_parse_10k(ticker)
    
    if chunks:
        print(f"\n{'='*60}")
        print("SAMPLE CHUNKS:")
        print('='*60)
        
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\nChunk {i} ({len(chunk.split())} words):")
            print(chunk[:300] + "...")
        
        print(f"\n✓ Successfully parsed {ticker} 10-K into {len(chunks)} chunks")
    else:
        print(f"\n✗ Failed to parse {ticker}")