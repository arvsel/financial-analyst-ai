"""
fetch_sec_filing.py
This script fetches SEC filing data and demonstrates file handling
"""

# ============================================================
# IMPORTS
# ============================================================
import requests
import json
import time
import os


# ============================================================
# FUNCTIONS
# ============================================================

def fetch_company_info(ticker):
    """
    Fetch basic company information from SEC EDGAR API
    """
    print(f"Fetching data for {ticker}...")
    
    # SEC requires a User-Agent header (identifies who is making the request)
    headers = {
        'User-Agent': 'Financial Analyst AI arvindselvakesari@example.com'
    }
    
    # Build the API URL
    url = "https://www.sec.gov/cgi-bin/browse-edgar"
    
    # Parameters for the request
    params = {
        'action': 'getcompany',
        'CIK': ticker,
        'type': '10-K',
        'dateb': '20241231',
        'owner': 'exclude',
        'output': 'atom',
        'count': 1
    }
    
    # Make the request to the SEC website
    response = requests.get(url, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        print(f"✓ Successfully fetched data for {ticker}")
        return response.text
    else:
        print(f"✗ Error: {response.status_code}")
        return None


def read_filing(ticker):
    """
    Read a filing from disk
    """
    filename = f"{ticker}_filing.xml"
    
    try:
        with open(filename, "r") as file:
            content = file.read()
        print(f"✓ Read {len(content)} characters from {filename}")
        return content
    except FileNotFoundError:
        print(f"✗ File {filename} not found!")
        return None


def smart_fetch(ticker):
    """
    Check if file exists first, only fetch if needed
    This saves time and bandwidth by using cached files
    """
    filename = f"{ticker}_filing.xml"
    
    # Check if file already exists
    if os.path.exists(filename):
        print(f"📁 File {filename} already exists, reading from disk...")
        with open(filename, "r") as file:
            content = file.read()
        print(f"✓ Loaded {len(content)} characters from {filename}")
        return content
    else:
        print(f"🌐 File not found, fetching from SEC...")
        data = fetch_company_info(ticker)
        
        if data:
            with open(filename, "w") as file:
                file.write(data)
            print(f"✓ Saved to {filename}")
            return data
        else:
            return None


def smart_fetch_with_expiry(ticker, max_age_days=1):
    """
    BONUS: Check if file exists AND is recent, only fetch if needed
    Only uses cached files that are less than max_age_days old
    """
    filename = f"{ticker}_filing.xml"
    
    if os.path.exists(filename):
        # Check file age
        import datetime
        file_time = os.path.getmtime(filename)
        file_age_seconds = time.time() - file_time
        file_age_days = file_age_seconds / (60 * 60 * 24)
        
        if file_age_days < max_age_days:
            print(f"📁 Using cached file (age: {file_age_days:.1f} days)...")
            with open(filename, "r") as file:
                return file.read()
        else:
            print(f"⏰ Cached file too old ({file_age_days:.1f} days), re-fetching...")
    else:
        print(f"🌐 No cached file, fetching from SEC...")
    
    # Fetch fresh data
    data = fetch_company_info(ticker)
    if data:
        with open(filename, "w") as file:
            file.write(data)
        print(f"✓ Saved to {filename}")
    return data


# ============================================================
# MAIN CODE - This runs when you execute the file
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SEC FILING FETCHER - DEMO")
    print("="*60)
    
    # Task 1: Fetch multiple companies
    print("\n--- TASK 1: Fetch Multiple Companies ---")
    tickers = ["MSFT", "AAPL", "GOOGL"]
    
    for ticker in tickers:
        print(f"\n{'='*50}")
        data = fetch_company_info(ticker)
        
        if data:
            filename = f"{ticker}_filing.xml"
            with open(filename, "w") as file:
                file.write(data)
            print(f"✓ Saved to {filename}")
        
        time.sleep(1)  # Be nice to SEC servers
    
    print(f"\n{'='*50}")
    print("✓ Done fetching all companies!")
    
    # Task 2: Test reading a file
    print("\n--- TASK 2: Test Reading Function ---")
    msft_data = read_filing("MSFT")
    if msft_data:
        print(f"First 200 characters: {msft_data[:200]}...")
    
    # Task 3: Test error handling
    print("\n--- TASK 3: Test Error Handling ---")
    tesla_data = read_filing("TSLA")  # This should fail
    
    # Bonus Challenge: Test smart fetch
    print("\n" + "="*60)
    print("BONUS: TESTING SMART FETCH")
    print("="*60)
    
    # First call - might fetch or read from disk
    print("\n--- First call (MSFT) ---")
    data1 = smart_fetch("MSFT")
    
    time.sleep(1)
    
    # Second call - should read from disk
    print("\n--- Second call (MSFT again) ---")
    data2 = smart_fetch("MSFT")
    
    # Try a new company
    print("\n--- New company (NVDA) ---")
    data3 = smart_fetch("NVDA")
    
    time.sleep(1)
    
    # Try reading NVDA again
    print("\n--- NVDA again ---")
    data4 = smart_fetch("NVDA")
    
    print("\n" + "="*60)
    print("✓ All tests complete!")
    print("="*60)
    
    # Show what files were created
    print("\nFiles created in this directory:")
    xml_files = [f for f in os.listdir('.') if f.endswith('_filing.xml')]
    for f in xml_files:
        file_size = os.path.getsize(f)
        print(f"  - {f} ({file_size:,} bytes)")