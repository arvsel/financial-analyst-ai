"""
Advanced 10-K parser that extracts specific sections from HTML
"""

from sec_edgar_downloader import Downloader
import os
import re
import html
from bs4 import BeautifulSoup

def clean_text(content):
    """Clean text extracted from HTML"""
    # Decode HTML entities
    text = html.unescape(content)
    
    # Remove excessive whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\t+', ' ', text)
    
    return text.strip()

def find_primary_document(folder_path):
    """Find the main 10-K document"""
    # First priority: look for primary-document.html
    primary_doc = os.path.join(folder_path, "primary-document.html")
    if os.path.exists(primary_doc):
        print(f"   Using primary-document.html")
        return primary_doc
    
    # Second: look for any .htm file with the ticker in the name
    for filename in os.listdir(folder_path):
        if filename.endswith('.htm') or filename.endswith('.html'):
            if 'index' not in filename.lower():
                return os.path.join(folder_path, filename)
    
    # Fallback
    return os.path.join(folder_path, "full-submission.txt")

def extract_10k_sections(html_content):
    """Extract sections from 10-K HTML - improved version"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get all text
    full_text = soup.get_text(separator='\n')
    
    sections = {}
    
    # Multiple pattern variations for each section
    section_patterns = {
        'business': [
            r'ITEM\s*1\b[^A].*?BUSINESS',
            r'Item\s*1\b[^A].*?Business',
            r'ITEM\s*1\s*\n.*?BUSINESS',
        ],
        'risk_factors': [
            r'ITEM\s*1A\b.*?RISK\s*FACTORS',
            r'Item\s*1A\b.*?Risk\s*Factors',
            r'ITEM\s*1A\s*\n.*?RISK',
        ],
        'md_and_a': [
            r'ITEM\s*7\b.*?MANAGEMENT',
            r'Item\s*7\b.*?Management',
        ],
        'financial_statements': [
            r'ITEM\s*8\b.*?FINANCIAL\s*STATEMENTS',
            r'Item\s*8\b.*?Financial\s*Statements',
        ],
    }
    
    # Find ALL matches for each pattern (not just first)
    section_candidates = {}
    
    for section_name, patterns in section_patterns.items():
        all_matches = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, full_text, re.IGNORECASE | re.DOTALL))
            all_matches.extend(matches)
        
        if all_matches:
            # Sort by position
            all_matches.sort(key=lambda x: x.start())
            
            # Usually the LAST match is the actual section (after TOC)
            # But if there's only one match, use it
            if len(all_matches) == 1:
                best_match = all_matches[0]
            else:
                # Filter out matches in first 50K (likely TOC)
                main_matches = [m for m in all_matches if m.start() > 50000]
                best_match = main_matches[0] if main_matches else all_matches[-1]
            
            section_candidates[section_name] = best_match.start()
            print(f"   ✓ Found: {section_name} at position {best_match.start():,} (from {len(all_matches)} total matches)")
    
    if not section_candidates:
        print("   ⚠️  No sections found, using full document")
        cleaned = clean_text(full_text)
        return {'full_document': cleaned} if len(cleaned) > 1000 else {}
    
    # Sort by position
    sorted_sections = sorted(section_candidates.items(), key=lambda x: x[1])
    
    # Extract text between sections
    for i, (section_name, start_pos) in enumerate(sorted_sections):
        if i < len(sorted_sections) - 1:
            end_pos = sorted_sections[i + 1][1]
        else:
            # Take up to 300K chars or end of doc
            end_pos = min(start_pos + 300000, len(full_text))
        
        section_text = full_text[start_pos:end_pos]
        section_text = clean_text(section_text)
        
        # Only keep substantial sections
        if len(section_text) > 1000:
            sections[section_name] = section_text
            print(f"   → Extracted: {section_name} ({len(section_text):,} chars)")
    
    return sections
    
    # Find sections - skip first 50,000 chars (usually table of contents)
    section_positions = {}
    search_start = 50000  # Skip TOC
    
    for section_name, patterns in section_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, full_text[search_start:], re.IGNORECASE)
            if match:
                actual_position = search_start + match.start()
                section_positions[section_name] = actual_position
                print(f"   ✓ Found: {section_name} at position {actual_position:,}")
                break
    
    if not section_positions:
        print("   ⚠️  No sections found after TOC")
        # Try without skipping TOC
        print("   Trying full document search...")
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
                if len(matches) > 1:
                    # Take the last match (likely the actual section, not TOC)
                    actual_position = matches[-1].start()
                    section_positions[section_name] = actual_position
                    print(f"   ✓ Found: {section_name} at position {actual_position:,}")
                    break
    
    if not section_positions:
        print("   ⚠️  No standard sections found")
        print("   Using full document")
        cleaned = clean_text(full_text)
        if len(cleaned) > 1000:
            return {'full_document': cleaned}
        else:
            return {}
    
    # Sort by position
    sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])
    
    # Extract text between sections
    for i, (section_name, start_pos) in enumerate(sorted_sections):
        if i < len(sorted_sections) - 1:
            end_pos = sorted_sections[i + 1][1]
        else:
            # Take substantial chunk or end of doc
            end_pos = min(start_pos + 200000, len(full_text))
        
        section_text = full_text[start_pos:end_pos]
        section_text = clean_text(section_text)
        
        # Only keep if substantial
        if len(section_text) > 1000:
            sections[section_name] = section_text
    
    return sections
    
    # Find sections
    section_positions = {}
    
    for section_name, patterns in section_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                section_positions[section_name] = match.start()
                print(f"   ✓ Found: {section_name} at position {match.start():,}")
                break  # Stop after first match
    
    if not section_positions:
        print("   ⚠️  No standard sections found")
        print("   Using full document (this is okay for testing)")
        # Return full document as fallback
        cleaned = clean_text(full_text)
        if len(cleaned) > 1000:
            return {'full_document': cleaned}
        else:
            return {}
    
    # Sort by position
    sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])
    
    # Extract text between sections
    for i, (section_name, start_pos) in enumerate(sorted_sections):
        if i < len(sorted_sections) - 1:
            end_pos = sorted_sections[i + 1][1]
        else:
            # Take next 100,000 chars or end of doc
            end_pos = min(start_pos + 100000, len(full_text))
        
        section_text = full_text[start_pos:end_pos]
        section_text = clean_text(section_text)
        
        if len(section_text) > 500:
            sections[section_name] = section_text
    
    return sections

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.split()) > 50:
            chunks.append(chunk)
    
    return chunks

def fetch_and_parse_10k_sections(ticker):
    """Download and parse 10-K sections"""
    print(f"\n{'='*60}")
    print(f"Processing {ticker}")
    print('='*60)
    
    # Download
    dl = Downloader("FinancialAnalystAI", "arvindselvakesari@example.com")
    
    print("Step 1: Downloading latest 10-K from SEC...")
    try:
        dl.get("10-K", ticker, limit=1, download_details=True)
    except Exception as e:
        print(f"✗ Error: {e}")
        return []
    
    # Find folder
    base_path = "sec-edgar-filings"
    ticker_path = os.path.join(base_path, ticker, "10-K")
    
    filing_folders = sorted(
        [f for f in os.listdir(ticker_path) if os.path.isdir(os.path.join(ticker_path, f))],
        reverse=True
    )
    latest_folder = filing_folders[0]
    folder_path = os.path.join(ticker_path, latest_folder)
    
    print(f"✓ Found filing: {latest_folder}")
    
    # Find primary document
    print("\nStep 2: Finding primary document...")
    doc_path = find_primary_document(folder_path)
    print(f"✓ Using: {os.path.basename(doc_path)}")
    
    # Read and parse
    print("\nStep 3: Extracting sections...")
    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    sections = extract_10k_sections(content)
    
    if not sections:
        print("✗ No sections extracted")
        return []
    
    print(f"\n✓ Extracted {len(sections)} section(s):")
    for section_name, section_text in sections.items():
        print(f"   - {section_name}: {len(section_text):,} characters")
    
    # Chunk with metadata
    print("\nStep 4: Creating chunks with metadata...")
    all_chunks = []
    
    for section_name, section_text in sections.items():
        section_chunks = chunk_text(section_text, chunk_size=500, overlap=50)
        
        for i, chunk in enumerate(section_chunks):
            all_chunks.append({
                'text': chunk,
                'section': section_name,
                'chunk_id': i,
                'ticker': ticker
            })
        
        print(f"   - {section_name}: {len(section_chunks)} chunks")
    
    print(f"\n✓ Total: {len(all_chunks)} chunks")
    
    return all_chunks

# Test
if __name__ == "__main__":
    ticker = "MSFT"
    chunks = fetch_and_parse_10k_sections(ticker)
    
    if chunks:
        print(f"\n{'='*60}")
        print("SAMPLE CHUNKS:")
        print('='*60)
        
        # Show samples from each section
        seen_sections = set()
        for chunk in chunks:
            section = chunk['section']
            if section not in seen_sections:
                print(f"\n[{section.upper().replace('_', ' ')}]")
                print(chunk['text'][:250] + "...")
                seen_sections.add(section)
                
                if len(seen_sections) >= 3:
                    break