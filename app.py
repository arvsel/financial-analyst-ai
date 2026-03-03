"""
Financial Analyst AI - Streamlit Web Interface (Dark Theme)
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

load_dotenv()

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
</style>
""", unsafe_allow_html=True)

# Initialize clients
@st.cache_resource
def init_clients():
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    return pc, openai_client, anthropic_client

pc, openai_client, anthropic_client = init_clients()
INDEX_NAME = "financial-docs"

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

def upload_document(text, ticker, doc_type="custom"):
    """Upload document to Pinecone with error handling"""
    
    chunks = chunk_text(text)
    
    if not chunks:
        st.error("No chunks created! Text might be too short.")
        return 0
    
    st.info(f"✨ Created {len(chunks)} chunks from document")
    
    index = pc.Index(INDEX_NAME)
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
    st.metric("🏢 Companies", "3+", delta="MSFT, AAPL, TSLA", help="Indexed companies")

with col2:
    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    st.metric("📄 Chunks", f"{stats['total_vector_count']:,}", delta="Live", help="Total document chunks")

with col3:
    st.metric("🤖 AI Model", "Claude 4", delta="Latest", help="Anthropic Claude Sonnet 4")

with col4:
    st.metric("🔍 Dimensions", "768", delta="Embeddings", help="OpenAI text-embedding-3-small")

st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📤 Upload Documents", "⚖️ Compare Companies"])

# ==================== TAB 1: ASK QUESTIONS ====================
with tab1:
    # Sidebar filters
    st.sidebar.header("🔍 Search Filters")
    
    ticker_filter = st.sidebar.selectbox(
        "Company",
        ["All Companies", "MSFT", "AAPL", "TSLA"],
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
                            badge_color = "#10B981"
                        elif relevance >= 0.6:
                            emoji = "🟡"
                            badge_color = "#FBBF24"
                        else:
                            emoji = "🔴"
                            badge_color = "#EF4444"
                        
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
            top_k=10,
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
    
    # Company selection
    col1, col2 = st.columns(2)
    
    with col1:
        companies_to_compare = st.multiselect(
            "Select companies to compare (2-4)",
            ["MSFT", "AAPL", "TSLA"],
            default=["MSFT", "AAPL"],
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
    
    # Comparison depth
    comparison_depth = st.select_slider(
        "Analysis depth",
        options=["Quick Summary", "Standard Analysis", "Deep Dive"],
        value="Standard Analysis",
        help="More depth = longer, more detailed analysis"
    )
    
    # Run comparison
    if st.button("🔍 Generate Comparison", type="primary", use_container_width=True):
        if len(companies_to_compare) < 2:
            st.warning("⚠️ Please select at least 2 companies to compare!")
        elif not comparison_aspects:
            st.warning("⚠️ Please select at least one aspect to compare!")
        else:
            with st.spinner(f"🔄 Analyzing {len(companies_to_compare)} companies across {len(comparison_aspects)} dimensions..."):
                
                # Gather information for each company
                company_data = {}
                
                for ticker in companies_to_compare:
                    st.markdown(f"**Gathering data for {ticker}...**")
                    company_info = {}
                    
                    for aspect in comparison_aspects:
                        # Create targeted query for this aspect
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
                        
                        # Search for this company and aspect
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
                        
                        # Collect relevant text
                        aspect_text = "\n".join([
                            match['metadata']['text']
                            for match in results['matches']
                        ])
                        
                        company_info[aspect] = aspect_text
                    
                    company_data[ticker] = company_info
                
                # Generate comparison with Claude
                st.markdown("**Generating AI comparison...**")
                
                # Build comparison prompt
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
                
                # Display results
                st.success("✅ Comparison complete!")
                
                st.markdown("---")
                st.markdown("### 📊 Comparative Analysis")
                st.markdown(f"**Companies:** {', '.join(companies_to_compare)}")
                st.markdown(f"**Aspects:** {', '.join(comparison_aspects)}")
                st.markdown("---")
                
                st.markdown(comparison_result)
                
                # Download button
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
    
    # Example comparisons
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
        - Companies: All three
        - Focus: Risk Factors, Market Position
        - Perfect for: Due diligence and investment decisions
        """)

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

**📈 Capabilities:**
- Real-time SEC filing analysis
- Custom document upload
- Section-aware filtering
- Citation-backed answers

**💡 Pro Tips:**
- Use filters for targeted search
- Upload your own reports
- Check relevance scores
- Expand sources for full context
""")

st.sidebar.markdown("---")
st.sidebar.markdown("*Built with ❤️ for financial analysis*")