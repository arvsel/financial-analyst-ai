# This is a comment - Python ignores these lines
# They're just notes for humans

# Variables - containers for data
company = "Microsoft"  # String (text)
revenue = 211900  # Number (in millions)
is_profitable = True  # Boolean (True/False)

# Print to console
print(f"{company} had revenue of ${revenue}M")

# Lists - ordered collections
tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN","NVDA","META","TSLA"]
print(f"My watchlist: {tech_stocks}")

# Accessing list items (starts at 0)
first_stock = tech_stocks[0]
print(f"First stock: {first_stock}")

# Loops - do something repeatedly
for stock in tech_stocks:
    print(f"Analyzing {stock}...")

# Dictionaries - key-value pairs
company_info = {
    "ticker": "MSFT",
    "name": "Microsoft",
    "sector": "Technology"
}
print(f"Ticker: {company_info['ticker']}")

# Functions - reusable blocks of code
def calculate_market_cap(price, shares_outstanding):
    market_cap = price * shares_outstanding
    return market_cap

def calculate_pe_ratio(price, earnings):
    """Calculate Price-to-Earnings ratio"""
    pe_ratio = price / earnings
    return pe_ratio

msft_market_cap = calculate_market_cap(420, 7.43e9)
print(f"MSFT Market Cap: ${msft_market_cap / 1e12:.2f}T")

msft_pe = calculate_pe_ratio(420, 11.86)
print(f"MSFT P/E Ratio: {msft_pe:.2f}")

# Dictionary of companies with price and earnings
companies = {
    "MSFT": {"price": 420, "earnings": 11.86},
    "AAPL": {"price": 185, "earnings": 6.13},
    "GOOGL": {"price": 145, "earnings": 5.80}
}

# Loop through and calculate P/E for each
print("\nP/E Ratios:")
for ticker, data in companies.items():
    pe = calculate_pe_ratio(data["price"], data["earnings"])
    print(f"{ticker}: {pe:.2f}")