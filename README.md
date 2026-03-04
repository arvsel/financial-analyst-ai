# 📊 Financial Analyst AI

AI-powered SEC filing analysis tool with real-time insights and citation-backed answers.

🔗 **Live Demo:** https://financial-analyst-ai-v1.streamlit.app/

## Features

- 🔍 **Question Answering** - Ask questions about SEC 10-K filings with AI-generated answers
- 📤 **Document Upload** - Upload custom earnings reports, press releases, or analyst reports
- 🏢 **Auto-Fetch SEC Filings** - Automatically download and index any company's latest 10-K
- ⚖️ **Company Comparison** - Side-by-side analysis of multiple companies
- 📊 **Visual Analytics** - AI-powered revenue charts and margin analysis
- 🎯 **Section Filtering** - Search specific sections (Business, Risk Factors, MD&A, Financials)

## Tech Stack

- **AI Models:** Claude Sonnet 4 (Anthropic), OpenAI Embeddings
- **Vector Database:** Pinecone (768-dimensional embeddings)
- **Web Framework:** Streamlit
- **Visualizations:** Plotly
- **Data Source:** SEC EDGAR API

## Indexed Companies

- Microsoft (MSFT)
- Apple (AAPL)
- Tesla (TSLA)
- _+ Upload your own documents_

## Architecture

1. **Data Ingestion:** SEC filings downloaded and parsed into sections
2. **Embedding:** Text chunks converted to 768-dim vectors via OpenAI
3. **Storage:** Vectors stored in Pinecone with metadata (ticker, section, chunk_id)
4. **Retrieval:** Semantic search finds relevant chunks for user queries
5. **Generation:** Claude generates answers with citations from retrieved context

## Local Development
```bash
# Clone repository
git clone https://github.com/arvsel/financial-analyst-ai.git
cd financial-analyst-ai

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add API keys to .env
PINECONE_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Run app
streamlit run app.py
```

## Project Structure
```
financial-analyst-ai/
├── app.py                      # Main Streamlit application
├── parse_10k_sections.py       # SEC filing parser
├── load_with_sections.py       # Upload script for Pinecone
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version for deployment
└── .streamlit/secrets.toml     # API keys (not in repo)
```

## Deployment

Deployed on Streamlit Cloud with automatic CI/CD from GitHub.

## Author

Built by Arvind Selvakesari
- 💼 Insights & Analytics Manager @ U.S. Bank
- 🎓 MBA, Babson College
- 🚀 Angel Investor, Chennai Angels

---

⭐ Star this repo if you find it useful!
