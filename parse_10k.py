"""
Parse SEC 10-K filings using SEC's text extraction
"""

import requests
import re
import time

def get_latest_10k_facts(ticker):
    """
    Get latest 10-K using SEC Company Facts API
    """
    headers = {'User-Agent': 'Financial Analyst AI arvindselvakesari@example.com'}
    
    # Get CIK (company identifier)
    cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': ticker,
        'type': '10-K',
        'dateb': '',
        'count': 1,
        'output': 'atom'
    }
    
    response = requests.get(cik_url, headers=headers, params=params)
    
    # Extract CIK from response
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response.content)
    
    # Find CIK in the feed
    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        for elem in entry:
            if 'cik' in elem.tag.lower():
                cik = elem.text
                return cik.zfill(10)  # Pad with zeros
    
    return None

def get_filing_text_url(ticker):
    """
    Get the full text submission URL for latest 10-K
    """
    headers = {'User-Agent': 'Financial Analyst AI arvindselvakesari@example.com'}
    
    # Get recent filings
    url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'CIK': ticker,
        'type': '10-K',
        'dateb': '',
        'owner': 'exclude',
        'count': 10
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    # Parse HTML to find accession number
    import re
    pattern = r'edgar/data/\d+/(\d{10}-\d{2}-\d{6})'
    matches = re.findall(pattern, response.text)
    
    if not matches:
        return None
    
    # Get the first (most recent) filing
    accession = matches[0]
    accession_no_dashes = accession.replace('-', '')
    
    # Get CIK
    cik_pattern = r'edgar/data/(\d+)/'
    cik_match = re.search(cik_pattern, response.text)
    if not cik_match:
        return None
    
    cik = cik_match.group(1)
    
    # Build URL to the full text submission
    text_url = f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession}&xbrl_type=v"
    
    # Actually, let's use the simpler complete submission text file
    text_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{accession}.txt"
    
    return text_url

def extract_text_from_submission(content):
    """
    Extract text from SEC complete submission file
    """
    # Decode if bytes
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')
    
    # The .txt file contains the entire submission
    # Let's extract just the main document text
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', content)
    
    # Remove excessive whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove special characters and control characters
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    
    return text.strip()

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Split text into overlapping chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.split()) > 50:  # Only keep chunks with at least 50 words
            chunks.append(chunk)
    
    return chunks

def fetch_and_parse_10k(ticker):
    """
    Complete pipeline: fetch latest 10-K and parse
    """
    print(f"\n{'='*60}")
    print(f"Processing {ticker}")
    print('='*60)
    
    # Step 1: Get filing URL
    print("Step 1: Finding latest 10-K...")
    url = get_filing_text_url(ticker)
    
    if not url:
        print(f"✗ Could not find 10-K for {ticker}")
        return []
    
    print(f"✓ Found: {url[:80]}...")
    
    # Step 2: Download
    print("Step 2: Downloading...")
    headers = {'User-Agent': 'Financial Analyst AI arvindselvakesari@example.com'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"✗ Error downloading: {e}")
        return []
    
    # Step 3: Extract text
    print("Step 3: Extracting text...")
    text = extract_text_from_submission(response.content)
    print(f"✓ Extracted {len(text):,} characters")
    
    # Step 4: Chunk
    print("Step 4: Creating chunks...")
    chunks = chunk_text(text, chunk_size=800, overlap=100)
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