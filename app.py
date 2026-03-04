"""
Financial Analyst AI - Streamlit Web Interface (Dark Theme + Visualizations)
"""

import streamlit as st
import os
from pinecone import Pinecone
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
import html
import time
import plotly.graph_objects as go
import plotly.express as px
import json

load_dotenv()

# Load secrets from Streamlit Cloud or .env file
def get_secret(key):
    """Get secret from Streamlit secrets or environment variable"""
    try:
        return st.secrets[key]
    except:
        return os.getenv(key)

# Page config
st.set_page_config(
    page_title="Financial Analyst AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Dark theme colors */
    :root {
        --primary-color: #3B82F6;
        --secondary-color: #8B5CF6;
        --background-color: #0F172A;
        --secondary-background: #1E293B;
        --card-background: #334155;
        --text-color: #F1F5F9;
        --border-color: #475569;
    }
    
    /* Main background */
    .stApp {
        background-color: #0F172A;
        color: #F1F5F9;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Headers */
    h1 {
        color: #60A5FA !important;
        font-weight: 700 !important;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3B82F6;
        text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
    }
    
    h2 {
        color: #E0E7FF !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: #93C5FD !important;
        font-weight: 500 !important;
    }
    
    /* All text */
    p, div, span, label {
        color: #E2E8F0 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1E293B !important;
        border-radius: 10px;
        border: 2px solid #475569 !important;
        padding: 0.75rem;
        color: #F1F5F9 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #60A5FA !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #60A5FA;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
    }
    
    /* Metric container */
    [data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    
    /* Success/Error/Info messages */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 8px;
        color: #6EE7B7 !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        padding: 1rem;
        border-radius: 8px;
        color: #FCA5A5 !important;
    }
    
    .stInfo {
        background-color: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 8px;
        color: #93C5FD !important;
    }
    
    .stWarning {
        background-color: rgba(251, 191, 36, 0.1);
        border-left: 4px solid #FBBF24;
        padding: 1rem;
        border-radius: 8px;
        color: #FCD34D !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1E293B;
        border-radius: 10px;
        border: 1px solid #475569;
        font-weight: 500;
        color: #E2E8F0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #334155;
        border-color: #3B82F6;
    }
    
    .streamlit-expanderContent {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-top: none;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E293B;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #94A3B8;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #3B82F6;
        border-radius: 12px;
        padding: 2rem;
        background-color: #1E293B;
    }
    
    [data-testid="stFileUploader"] label {
        color: #E2E8F0 !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #1E293B !important;
        border-radius: 10px;
        border: 2px solid #475569 !important;
        color: #F1F5F9 !important;
    }
    
    /* Selectbox dropdown */
    [data-baseweb="select"] {
        background-color: #1E293B !important;
    }
    
    [data-baseweb="popover"] {
        background-color: #1E293B !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #3B82F6;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #3B82F6 !important;
    }
    
    /* Horizontal rule */
    hr {
        border-color: #334155;
    }
    
    /* Code blocks */
    code {
        background-color: #1E293B;
        color: #93C5FD;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
    
    /* Markdown */
    [data-testid="stMarkdownContainer"] {
        color: #E2E8F0;
    }
    
    /* Links */
    a {
        color: #60A5FA !important;
    }
    
    a:hover {
        color: #93C5FD !important;
    }
    
    /* Checkbox */
    .stCheckbox {
        color: #E2E8F0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize clients
@st.cache_resource
def init_clients():
    pc = Pinecone(api_key=get_secret('PINECONE_API_KEY'))
    openai_client = OpenAI(api_key=get_secret('OPENAI_API_KEY'))
    anthropic_client = Anthropic(api_key=get_secret('ANTHROPIC_API_KEY'))
    return pc, openai_client, anthropic_client

pc, openai_client, anthropic_client = init_clients()
INDEX_NAME = "financial-docs"
index = pc.Index(INDEX_NAME)

# Helper functions
def clean_text(content):
    """Clean uploaded text"""
    text = html.unescape(content)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.split()) > 20:
            chunks.append(chunk)
    return chunks

def format_number(value):
    """Format large numbers into readable strings"""
    if value is None:
        return "N/A"
    
    if value >= 1000:
        return f"${value/1000:.1f}B"
    elif value >= 1:
        return f"${value:.1f}M"
    else:
        return f"${value:.2f}M"

def upload_document(text, ticker, doc_type="custom"):
    """Upload document to Pinecone with error handling"""
    
    chunks = chunk_text(text)
    
    if not chunks:
        st.error("No chunks created! Text might be too short.")
        return 0
    
    st.info(f"✨ Created {len(chunks)} chunks from document")
    
    vectors = []
    uploaded_count = 0
    
    for i, chunk in enumerate(chunks):
        try:
            response = openai_client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small",
                dimensions=768
            )
            embedding = response.data[0].embedding
            
            vector_id = f"{ticker}_custom_{int(time.time())}_{i}"
            
            vector = (
                vector_id,
                embedding,
                {
                    'text': chunk,
                    'ticker': ticker,
                    'section': 'custom',
                    'chunk_id': i,
                    'doc_type': doc_type
                }
            )
            vectors.append(vector)
            
        except Exception as e:
            st.warning(f"⚠️ Error creating embedding for chunk {i}: {str(e)}")
            continue
    
    try:
        if vectors:
            index.upsert(vectors=vectors)
            uploaded_count = len(vectors)
            st.success(f"✅ Successfully uploaded {uploaded_count} vectors to Pinecone")
        else:
            st.error("❌ No vectors to upload!")
            
    except Exception as e:
        st.error(f"❌ Error uploading to Pinecone: {str(e)}")
        return 0
    
    return uploaded_count

def extract_metrics_with_ai(ticker):
    """Use AI to extract financial metrics from filings"""
    
    # Search for financial data
    queries = [
        "total revenue annual",
        "operating income profit margin",
        "net income earnings"
    ]
    
    all_context = []
    for query in queries:
        response = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-small",
            dimensions=768
        )
        query_embedding = response.data[0].embedding
        
        results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
            filter={'ticker': ticker}
        )
        
        for match in results['matches']:
            all_context.append(match['metadata']['text'])
    
    context = "\n\n".join(all_context)
    
    # Ask Claude to extract metrics
    prompt = f"""Extract financial metrics from the following SEC filing excerpts for {ticker}.

Context:
{context}

Extract revenue, operating income, operating margin, and net income for the last 3 fiscal years.

Return ONLY a valid JSON object (no markdown, no explanation) in this EXACT format:
{{
    "revenue": {{"FY2024": 245122, "FY2023": 211915, "FY2022": 198270}},
    "operating_income": {{"FY2024": 109433, "FY2023": 88523, "FY2022": 83383}},
    "operating_margin": {{"FY2024": 44.6, "FY2023": 41.8, "FY2022": 42.1}},
    "net_income": {{"FY2024": 88136, "FY2023": 72361, "FY2022": 72738}}
}}

Rules:
- All revenue/income values in MILLIONS (not billions)
- Operating margin as percentage (e.g., 44.6 for 44.6%)
- Use null if data not found
- Only numbers, no $ or B or M
- Match fiscal year labels from the text

JSON only:"""
    
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = message.content[0].text.strip()
    
    # Extract JSON from response
    try:
        # Remove markdown code blocks if present
        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        metrics = json.loads(response_text)
        return metrics
    except:
        return None

# Get available tickers dynamically
@st.cache_data(ttl=30)
def get_available_tickers():
    """Get unique tickers from database"""
    base_tickers = ["All Companies", "MSFT", "AAPL", "TSLA"]
    
    try:
        results = index.query(
            vector=[0.1] * 768,
            top_k=50,
            include_metadata=True
        )
        
        found_tickers = set()
        for match in results['matches']:
            ticker = match['metadata'].get('ticker')
            if ticker:
                found_tickers.add(ticker)
        
        all_tickers = ["All Companies"] + sorted(list(found_tickers))
        return all_tickers
        
    except:
        return base_tickers

# Enhanced Header
st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <h1 style='font-size: 3.5rem; margin-bottom: 0.5rem;'>
            📊 Financial Analyst AI
        </h1>
        <p style='font-size: 1.3rem; color: #94A3B8; margin-top: 0;'>
            AI-Powered SEC Filing Analysis • Real-Time Insights • Citation-Backed Answers
        </p>
    </div>
""", unsafe_allow_html=True)

# Stats Dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    ticker_count = len(get_available_tickers()) - 1
    st.metric("🏢 Companies", f"{ticker_count}", help="Indexed companies")

with col2:
    stats = index.describe_index_stats()
    st.metric("📄 Chunks", f"{stats['total_vector_count']:,}", delta="Live", help="Total document chunks")

with col3:
    st.metric("🤖 AI Model", "Claude 4", delta="Latest", help="Anthropic Claude Sonnet 4")

with col4:
    st.metric("🔍 Dimensions", "768", delta="Embeddings", help="OpenAI text-embedding-3-small")

st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask Questions", "📤 Upload Documents", "⚖️ Compare Companies", "📊 Visual Analytics"])

# ==================== TAB 1: ASK QUESTIONS ====================
with tab1:
    # Sidebar filters
    st.sidebar.header("🔍 Search Filters")
    
    ticker_options = get_available_tickers()
    ticker_filter = st.sidebar.selectbox(
        "Company",
        ticker_options,
        index=0
    )
    
    section_filter = st.sidebar.selectbox(
        "Section",
        ["All Sections", "business", "risk_factors", "md_and_a", "financial_statements", "custom"],
        index=0
    )
    
    ticker = None if ticker_filter == "All Companies" else ticker_filter
    section = None if section_filter == "All Sections" else section_filter
    
    # Quick questions
    st.markdown("### 💡 Quick Questions")
    st.markdown("Click any question below to get started!")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Revenue Analysis", use_container_width=True):
            st.session_state.question = "What are the main revenue sources and growth drivers?"
    
    with col2:
        if st.button("⚠️ Risk Assessment", use_container_width=True):
            st.session_state.question = "What are the key risk factors facing the company?"
    
    with col3:
        if st.button("🤖 AI Strategy", use_container_width=True):
            st.session_state.question = "How is the company investing in artificial intelligence?"
    
    with col4:
        if st.button("💰 Profitability", use_container_width=True):
            st.session_state.question = "What are the operating margins and profitability trends?"
    
    st.markdown("")
    
    # Question input
    question = st.text_area(
        "Your question:",
        value=st.session_state.get('question', ''),
        height=120,
        placeholder="e.g., What were Microsoft's main growth drivers in fiscal 2024?",
        help="Ask anything about the indexed SEC filings"
    )
    
    # Search button
    if st.button("🔍 Get AI-Powered Answer", type="primary", use_container_width=True):
        if not question:
            st.warning("⚠️ Please enter a question!")
        else:
            with st.spinner("🔄 Searching documents and generating answer..."):
                
                # Create query embedding
                response = openai_client.embeddings.create(
                    input=question,
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
                
                # Search
                results = index.query(
                    vector=query_embedding,
                    top_k=5,
                    include_metadata=True,
                    filter=filter_dict if filter_dict else None
                )
                
                # Extract docs
                docs = []
                for match in results['matches']:
                    docs.append({
                        'text': match['metadata']['text'],
                        'score': match['score'],
                        'section': match['metadata'].get('section', 'unknown'),
                        'ticker': match['metadata'].get('ticker', 'unknown'),
                    })
                
                if not docs:
                    st.error("❌ No relevant documents found. Try adjusting your filters.")
                else:
                    # Build context
                    context = "\n\n".join([
                        f"[Source {i+1} - {doc['ticker']} - {doc['section']}]\n{doc['text']}"
                        for i, doc in enumerate(docs)
                    ])
                    
                    # Create prompt
                    prompt = f"""Based on the following excerpts from SEC 10-K filings, please answer the question.

Context from filings:
{context}

Question: {question}

Please provide a clear, detailed answer based on the documents above. Cite which companies and sections you're referencing.

Answer:"""
                    
                    # Get answer
                    message = anthropic_client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=2048,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    answer = message.content[0].text
                    
                    # Display
                    st.success("✅ Answer generated successfully!")
                    
                    st.markdown("---")
                    st.markdown("### 💡 AI-Generated Answer")
                    st.markdown(answer)
                    
                    st.markdown("---")
                    st.markdown("### 📚 Source Documents")
                    
                    for i, doc in enumerate(docs, 1):
                        # Visual relevance indicator
                        relevance = doc['score']
                        if relevance >= 0.8:
                            emoji = "🟢"
                        elif relevance >= 0.6:
                            emoji = "🟡"
                        else:
                            emoji = "🔴"
                        
                        with st.expander(f"{emoji} Source {i}: {doc['ticker']} - {doc['section'].upper().replace('_', ' ')} (Relevance: {doc['score']:.1%})"):
                            st.markdown(f"**Relevance Score:** {doc['score']:.1%}")
                            st.progress(doc['score'])
                            st.markdown("---")
                            st.markdown(doc['text'])

# ==================== TAB 2: UPLOAD DOCUMENTS ====================
with tab2:
    st.markdown("### 📤 Upload Your Own Documents")
    st.markdown("Upload earnings reports, press releases, or other financial documents to analyze.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'html', 'htm', 'rtf'],
            help="Supported formats: .txt, .html, .htm, .rtf"
        )
    
    with col2:
        upload_ticker = st.text_input(
            "Company Ticker",
            placeholder="e.g., TSLA",
            max_chars=10
        ).upper()
        
        upload_doc_type = st.selectbox(
            "Document Type",
            ["Earnings Report", "Press Release", "Analyst Report", "Other"]
        )
    
    # Process upload
    if uploaded_file and upload_ticker:
        if st.button("📥 Process and Upload", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing document..."):
                
                st.markdown("**📋 Debug Info:**")
                st.write(f"- File: {uploaded_file.name}")
                st.write(f"- Type: {uploaded_file.type}")
                st.write(f"- Size: {uploaded_file.size} bytes")
                
                try:
                    if uploaded_file.type == "text/plain":
                        text = uploaded_file.read().decode('utf-8')
                    elif 'rtf' in uploaded_file.type or uploaded_file.name.endswith('.rtf'):
                        content = uploaded_file.read().decode('utf-8', errors='ignore')
                        text = re.sub(r'\\[a-z]+\d*\s?', ' ', content)
                        text = re.sub(r'[{}]', '', text)
                        text = re.sub(r'\s+', ' ', text)
                    else:
                        html_content = uploaded_file.read().decode('utf-8')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text = soup.get_text(separator='\n')
                    
                    st.write(f"- Extracted: {len(text)} characters")
                    
                    text = clean_text(text)
                    st.write(f"- After cleaning: {len(text)} characters")
                    
                    num_chunks = upload_document(text, upload_ticker, upload_doc_type)
                    
                    if num_chunks > 0:
                        st.balloons()
                        st.success(f"🎉 Document uploaded successfully!")
                        st.info(f"💡 You can now search using ticker filter: **{upload_ticker}**")
                        
                        with st.expander("📄 Document Preview"):
                            st.text(text[:1000] + "..." if len(text) > 1000 else text)
                    else:
                        st.error("❌ Upload failed - 0 chunks created")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # Add new company from SEC
    st.markdown("---")
    st.markdown("### 🏢 Add New Company from SEC")
    st.markdown("Automatically fetch and index a company's latest 10-K filing from SEC EDGAR.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        new_ticker = st.text_input(
            "Enter Company Ticker",
            placeholder="e.g., NVDA, GOOGL, AMZN",
            max_chars=10,
            key="new_ticker_input"
        ).upper()
    
    with col2:
        st.markdown("**Supported filings:**")
        st.markdown("- Latest 10-K annual report")
        st.markdown("- Automatically extracts sections")
        st.markdown("- ~2-3 min processing time")
    
    if new_ticker:
        if st.button(f"📥 Fetch and Index {new_ticker} 10-K", type="primary", use_container_width=True):
            
            # Check if already exists
            test_results = index.query(
                vector=[0.1] * 768,
                top_k=1,
                include_metadata=True,
                filter={'ticker': new_ticker}
            )
            
            if test_results['matches']:
                st.warning(f"⚠️ {new_ticker} already exists in database. Proceeding will add more data.")
                proceed = st.checkbox(f"Add more data for {new_ticker} anyway?")
                if not proceed:
                    st.stop()
            
            with st.spinner(f"🔄 Fetching {new_ticker} 10-K from SEC EDGAR..."):
                try:
                    from parse_10k_sections import fetch_and_parse_10k_sections
                    
                    st.info("📡 Downloading from SEC...")
                    chunks = fetch_and_parse_10k_sections(new_ticker)
                    
                    if not chunks:
                        st.error(f"❌ Could not fetch 10-K for {new_ticker}. Ticker might be invalid or filing not available.")
                    else:
                        st.success(f"✅ Downloaded and parsed {len(chunks)} chunks!")
                        
                        st.info("☁️ Uploading to Pinecone...")
                        
                        vectors = []
                        uploaded_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, chunk_data in enumerate(chunks):
                            status_text.text(f"Processing chunk {i+1}/{len(chunks)}...")
                            progress_bar.progress((i + 1) / len(chunks))
                            
                            try:
                                response = openai_client.embeddings.create(
                                    input=chunk_data['text'],
                                    model="text-embedding-3-small",
                                    dimensions=768
                                )
                                embedding = response.data[0].embedding
                                
                                vector_id = f"{new_ticker}_{chunk_data['section']}_{chunk_data['chunk_id']}"
                                
                                vector = (
                                    vector_id,
                                    embedding,
                                    {
                                        'text': chunk_data['text'],
                                        'ticker': new_ticker,
                                        'section': chunk_data['section'],
                                        'chunk_id': chunk_data['chunk_id'],
                                        'doc_type': '10-K'
                                    }
                                )
                                vectors.append(vector)
                                
                                if len(vectors) >= 100:
                                    index.upsert(vectors=vectors)
                                    uploaded_count += len(vectors)
                                    vectors = []
                                
                            except Exception as e:
                                st.warning(f"⚠️ Error on chunk {i}: {str(e)}")
                                continue
                        
                        if vectors:
                            index.upsert(vectors=vectors)
                            uploaded_count += len(vectors)
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        st.balloons()
                        st.success(f"""🎉 Successfully added {new_ticker}!
                        
**Summary:**
- Total chunks uploaded: {uploaded_count}
- Sections extracted: {len(set(c['section'] for c in chunks))}
- Ready to query!

💡 **Next steps:**
1. Go to "Ask Questions" tab
2. Select "{new_ticker}" in company filter
3. Start asking questions!
                        """)
                        
                        with st.expander("📋 Sections Extracted"):
                            sections_found = {}
                            for chunk in chunks:
                                section = chunk['section']
                                sections_found[section] = sections_found.get(section, 0) + 1
                            
                            for section, count in sections_found.items():
                                st.write(f"- **{section.replace('_', ' ').title()}**: {count} chunks")
                        
                        st.cache_data.clear()
                
                except ImportError:
                    st.error("❌ Parser not found. Make sure `parse_10k_sections.py` exists in your project directory.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # Stats
    st.markdown("---")
    st.markdown("### 📊 Database Statistics")
    
    if st.button("🔄 Refresh Stats", use_container_width=True):
        stats = index.describe_index_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Vectors", f"{stats['total_vector_count']:,}")
        with col2:
            st.metric("Dimension", "768")
        
        st.markdown("#### 🔍 Sample Contents")
        
        results = index.query(
            vector=[0.1] * 768,
            top_k=20,
            include_metadata=True
        )
        
        tickers_found = {}
        for match in results['matches']:
            ticker = match['metadata'].get('ticker', 'unknown')
            section = match['metadata'].get('section', 'unknown')
            
            if ticker not in tickers_found:
                tickers_found[ticker] = []
            tickers_found[ticker].append(section)
        
        for ticker, sections in tickers_found.items():
            st.write(f"**{ticker}**: {len(sections)} chunks")
            st.write(f"  Sections: {set(sections)}")

# ==================== TAB 3: COMPARE COMPANIES ====================
with tab3:
    st.markdown("### ⚖️ Compare Companies Side-by-Side")
    st.markdown("Select companies and aspects to compare using AI-powered analysis.")
    
    col1, col2 = st.columns(2)
    
    available_companies = [t for t in ticker_options if t != "All Companies"]
    
    with col1:
        companies_to_compare = st.multiselect(
            "Select companies to compare (2-4)",
            available_companies,
            default=available_companies[:2] if len(available_companies) >= 2 else available_companies,
            max_selections=4,
            help="Choose 2-4 companies for comparison"
        )
    
    with col2:
        comparison_aspects = st.multiselect(
            "What to compare",
            [
                "Business Model",
                "Revenue Streams",
                "Risk Factors",
                "AI Strategy",
                "Profitability",
                "Growth Drivers",
                "Market Position"
            ],
            default=["Business Model", "Revenue Streams"],
            help="Select aspects to analyze"
        )
    
    comparison_depth = st.select_slider(
        "Analysis depth",
        options=["Quick Summary", "Standard Analysis", "Deep Dive"],
        value="Standard Analysis",
        help="More depth = longer, more detailed analysis"
    )
    
    if st.button("🔍 Generate Comparison", type="primary", use_container_width=True):
        if len(companies_to_compare) < 2:
            st.warning("⚠️ Please select at least 2 companies to compare!")
        elif not comparison_aspects:
            st.warning("⚠️ Please select at least one aspect to compare!")
        else:
            with st.spinner(f"🔄 Analyzing {len(companies_to_compare)} companies across {len(comparison_aspects)} dimensions..."):
                
                company_data = {}
                
                for ticker in companies_to_compare:
                    st.markdown(f"**Gathering data for {ticker}...**")
                    company_info = {}
                    
                    for aspect in comparison_aspects:
                        aspect_queries = {
                            "Business Model": "What is the core business model and how does the company make money?",
                            "Revenue Streams": "What are the main revenue sources and their contribution?",
                            "Risk Factors": "What are the key risk factors and challenges?",
                            "AI Strategy": "How is the company investing in and leveraging AI?",
                            "Profitability": "What are the profitability metrics and margins?",
                            "Growth Drivers": "What are driving growth and future opportunities?",
                            "Market Position": "What is the competitive position and market share?"
                        }
                        
                        query = aspect_queries.get(aspect, aspect)
                        
                        response = openai_client.embeddings.create(
                            input=query,
                            model="text-embedding-3-small",
                            dimensions=768
                        )
                        query_embedding = response.data[0].embedding
                        
                        results = index.query(
                            vector=query_embedding,
                            top_k=3,
                            include_metadata=True,
                            filter={'ticker': ticker}
                        )
                        
                        aspect_text = "\n".join([
                            match['metadata']['text']
                            for match in results['matches']
                        ])
                        
                        company_info[aspect] = aspect_text
                    
                    company_data[ticker] = company_info
                
                st.markdown("**Generating AI comparison...**")
                
                max_tokens = {
                    "Quick Summary": 1500,
                    "Standard Analysis": 3000,
                    "Deep Dive": 4000
                }
                
                comparison_context = ""
                for ticker, info in company_data.items():
                    comparison_context += f"\n\n{'='*60}\n{ticker} INFORMATION:\n{'='*60}\n"
                    for aspect, text in info.items():
                        comparison_context += f"\n{aspect}:\n{text[:500]}...\n"
                
                comparison_prompt = f"""You are a financial analyst comparing multiple companies. Provide a comprehensive comparison across the specified dimensions.

Companies to compare: {', '.join(companies_to_compare)}
Aspects to analyze: {', '.join(comparison_aspects)}

Data from SEC filings:
{comparison_context}

Please provide a structured comparison that:
1. Compares each aspect across all companies
2. Highlights key similarities and differences
3. Provides objective analysis based on the data
4. Uses clear sections for each comparison aspect
5. Concludes with overall positioning

Keep the analysis {"concise" if comparison_depth == "Quick Summary" else "detailed" if comparison_depth == "Standard Analysis" else "comprehensive and in-depth"}.

Comparison Analysis:"""
                
                message = anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=max_tokens[comparison_depth],
                    messages=[
                        {"role": "user", "content": comparison_prompt}
                    ]
                )
                
                comparison_result = message.content[0].text
                
                st.success("✅ Comparison complete!")
                
                st.markdown("---")
                st.markdown("### 📊 Comparative Analysis")
                st.markdown(f"**Companies:** {', '.join(companies_to_compare)}")
                st.markdown(f"**Aspects:** {', '.join(comparison_aspects)}")
                st.markdown("---")
                
                st.markdown(comparison_result)
                
                st.markdown("---")
                st.download_button(
                    label="📥 Download Comparison Report",
                    data=f"""COMPANY COMPARISON REPORT
{'='*60}

Companies: {', '.join(companies_to_compare)}
Aspects: {', '.join(comparison_aspects)}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}

{comparison_result}
""",
                    file_name=f"comparison_{'_'.join(companies_to_compare)}_{time.strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    
    st.markdown("---")
    st.markdown("### 💡 Example Comparisons")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Tech Giants Showdown**
        - Companies: MSFT vs AAPL
        - Focus: Business Model, Revenue, AI Strategy
        - Perfect for: Understanding ecosystem differences
        """)
    
    with col2:
        st.markdown("""
        **Risk Assessment**
        - Companies: All available
        - Focus: Risk Factors, Market Position
        - Perfect for: Due diligence and investment decisions
        """)

# ==================== TAB 4: VISUAL ANALYTICS ====================
with tab4:
    st.markdown("### 📊 Visual Analytics & Charts")
    st.markdown("AI-powered financial visualizations with automated metric extraction")
    
    # Chart type selection
    chart_type = st.radio(
        "Select visualization type:",
        ["Revenue Comparison", "Margin Analysis", "Custom Metrics"],
        horizontal=True
    )
    
    if chart_type == "Revenue Comparison":
        st.markdown("#### 📈 Revenue Comparison Chart")
        
        selected_companies = st.multiselect(
            "Select companies to visualize",
            [t for t in ticker_options if t != "All Companies"],
            default=[t for t in ticker_options if t != "All Companies"][:3]
        )
        
        if st.button("Generate Revenue Chart", type="primary", use_container_width=True):
            if not selected_companies:
                st.warning("⚠️ Please select at least one company")
            else:
                with st.spinner("🔄 Extracting financial data with AI..."):
                    
                    all_metrics = {}
                    for ticker in selected_companies:
                        metrics = extract_metrics_with_ai(ticker)
                        if metrics:
                            all_metrics[ticker] = metrics
                    
                    if not all_metrics:
                        st.error("❌ Could not extract metrics. Try adding more companies or check data availability.")
                    else:
                        # Create revenue chart
                        fig = go.Figure()
                        
                        for ticker, metrics in all_metrics.items():
                            if metrics and 'revenue' in metrics:
                                years = list(metrics['revenue'].keys())
                                values = [metrics['revenue'][year] for year in years if metrics['revenue'][year] is not None]
                                valid_years = [year for year in years if metrics['revenue'][year] is not None]
                                
                                if values:
                                    # Format values properly
                                    formatted_text = [format_number(v) for v in values]
                                    
                                    fig.add_trace(go.Bar(
                                        name=ticker,
                                        x=valid_years,
                                        y=values,
                                        text=formatted_text,
                                        textposition='auto',
                                    ))
                        
                        fig.update_layout(
                            title="Revenue Comparison Across Fiscal Years",
                            xaxis_title="Fiscal Year",
                            yaxis_title="Revenue (Millions USD)",
                            barmode='group',
                            template="plotly_dark",
                            height=500,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # AI Commentary
                        st.markdown("#### 🤖 AI Analysis")
                        
                        metrics_text = ""
                        for ticker, metrics in all_metrics.items():
                            if metrics and 'revenue' in metrics:
                                revenue_data = metrics['revenue']
                                metrics_text += f"\n{ticker} Revenue:\n"
                                for year, value in revenue_data.items():
                                    if value is not None:
                                        formatted_value = format_number(value)
                                        metrics_text += f"  - {year}: {formatted_value}\n"
                        
                        prompt = f"""Analyze the following revenue data and provide insights:

{metrics_text}

Provide a brief analysis (3-4 sentences) covering:
1. Revenue growth trends for each company
2. Year-over-year growth rates  
3. Key patterns or standout performers

CRITICAL: When writing dollar amounts, you MUST add spaces. Write "grew from 60.9 B to 215.9 B" not "60.9Bto215.9B".
"""
                        
                        message = anthropic_client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=500,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        
                        # Get the analysis
                        analysis_text = message.content[0].text
                        
                        # Comprehensive post-processing to fix formatting
                        # Step 1: Add space before "to" when numbers are stuck together
                        analysis_text = re.sub(r'(\d+\.?\d*[BMK])(to)(\d+\.?\d*[BMK])', r'\1 to \3', analysis_text, flags=re.IGNORECASE)
                        
                        # Step 2: Add space before B, M, K when stuck to numbers
                        analysis_text = re.sub(r'(\d+)([BMK])', r'\1 \2', analysis_text)
                        
                        # Step 3: Ensure $ before numbers with B/M/K
                        analysis_text = re.sub(r'(?<!\$)\b(\d+\.?\d*)\s*([BMK])\b', r'$\1\2', analysis_text)
                        
                        # Step 4: Fix "dollar X billion" patterns back to $XB
                        analysis_text = re.sub(r'dollar\s+(\d+(?:\.\d+)?)\s+billion', r'$\1B', analysis_text, flags=re.IGNORECASE)
                        analysis_text = re.sub(r'dollar\s+(\d+(?:\.\d+)?)\s+million', r'$\1M', analysis_text, flags=re.IGNORECASE)
                        
                        # Step 5: Remove any double spaces
                        analysis_text = re.sub(r'\s+', ' ', analysis_text)
                        
                        # Step 6: Fix "in FY2024 to a" patterns (remove extra text between numbers)
                        analysis_text = re.sub(r'in\s+FY\d{4}\s*to\s*a\s*projected\s*', 'to ', analysis_text, flags=re.IGNORECASE)
                        analysis_text = re.sub(r'in\s+FY\d{4}\s*to\s*', 'to ', analysis_text, flags=re.IGNORECASE)
                        
                        st.info(analysis_text)
    
    elif chart_type == "Margin Analysis":
        st.markdown("#### 💰 Operating Margin Trends")
        
        margin_company = st.selectbox(
            "Select company",
            [t for t in ticker_options if t != "All Companies"]
        )
        
        if st.button("Generate Margin Chart", type="primary", use_container_width=True):
            with st.spinner("🔄 Extracting margin data..."):
                
                metrics = extract_metrics_with_ai(margin_company)
                
                if not metrics or 'operating_margin' not in metrics:
                    st.error("❌ Could not extract margin data")
                else:
                    years = list(metrics['operating_margin'].keys())
                    margins = [metrics['operating_margin'][year] for year in years if metrics['operating_margin'][year] is not None]
                    valid_years = [year for year in years if metrics['operating_margin'][year] is not None]
                    
                    if not margins:
                        st.error("❌ No margin data available")
                    else:
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=valid_years,
                            y=margins,
                            mode='lines+markers',
                            name='Operating Margin',
                            line=dict(color='#3B82F6', width=3),
                            marker=dict(size=10),
                            text=[f"{m:.1f}%" for m in margins],
                            textposition='top center'
                        ))
                        
                        fig.update_layout(
                            title=f"{margin_company} Operating Margin Trend",
                            xaxis_title="Fiscal Year",
                            yaxis_title="Operating Margin (%)",
                            template="plotly_dark",
                            height=400,
                            yaxis=dict(ticksuffix="%")
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Metrics display
                        col1, col2, col3 = st.columns(3)
                        if len(margins) >= 1:
                            with col1:
                                st.metric("Latest Margin", f"{margins[-1]:.1f}%")
                        if len(margins) >= 2:
                            with col2:
                                change = margins[-1] - margins[-2]
                                st.metric("YoY Change", f"{change:+.1f}%", delta=f"{change:.1f}%")
                        if len(margins) >= 1:
                            with col3:
                                avg = sum(margins) / len(margins)
                                st.metric("Average", f"{avg:.1f}%")
    
    else:  # Custom Metrics
        st.markdown("#### 🎯 Custom Metric Visualization")
        st.info("💡 Ask Claude to extract and visualize specific metrics from filings")
        
        custom_ticker = st.selectbox(
            "Select company",
            [t for t in ticker_options if t != "All Companies"],
            key="custom_ticker"
        )
        
        metric_query = st.text_input(
            "What metric would you like to visualize?",
            placeholder="e.g., 'R&D spending over the years' or 'cloud revenue growth'"
        )
        
        if st.button("Generate Custom Visualization", type="primary", use_container_width=True):
            if not metric_query:
                st.warning("⚠️ Please enter a metric to visualize")
            else:
                with st.spinner("🔄 AI is extracting and visualizing data..."):
                    # Search for relevant data
                    response = openai_client.embeddings.create(
                        input=metric_query,
                        model="text-embedding-3-small",
                        dimensions=768
                    )
                    query_embedding = response.data[0].embedding
                    
                    results = index.query(
                        vector=query_embedding,
                        top_k=5,
                        include_metadata=True,
                        filter={'ticker': custom_ticker}
                    )
                    
                    context = "\n\n".join([
                        match['metadata']['text']
                        for match in results['matches']
                    ])
                    
                    # Ask Claude to extract and explain
                    prompt = f"""Extract numerical data for the following metric from the SEC filing excerpts:

Metric requested: {metric_query}
Company: {custom_ticker}

Context:
{context}

Please provide:
1. Any numerical values you can find (with years/periods)
2. A brief explanation of the trend or pattern
3. Key insights about this metric

If you cannot find specific numbers, explain what information is available."""
                    
                    message = anthropic_client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    st.markdown("### 📊 Analysis")
                    st.markdown(message.content[0].text)
                    
                    st.markdown("### 📚 Source Data")
                    with st.expander("View source excerpts"):
                        for i, match in enumerate(results['matches'][:3], 1):
                            st.markdown(f"**Source {i}:**")
                            st.markdown(match['metadata']['text'][:500] + "...")
                            st.markdown("---")

# Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 About This Tool")
st.sidebar.markdown("""
**Financial Analyst AI** uses cutting-edge AI to analyze SEC filings and 
provide instant insights with citations.

**🔧 Technology Stack:**
- 🧠 **Claude Sonnet 4** (Anthropic)
- 🔢 **OpenAI Embeddings** (768-dim)
- 🗄️ **Pinecone** Vector Database
- 🎨 **Streamlit** Web Framework
- 📊 **Plotly** Visualizations

**📈 Capabilities:**
- Real-time SEC filing analysis
- Custom document upload
- Auto-fetch from SEC EDGAR
- Section-aware filtering
- Citation-backed answers
- Company comparisons
- **Visual analytics & charts**

**💡 Pro Tips:**
- Use filters for targeted search
- Upload your own reports
- Add new companies from SEC
- Check relevance scores
- Download comparison reports
- Visualize financial metrics
""")

st.sidebar.markdown("---")
st.sidebar.markdown("*Built with ❤️ for financial analysis*")