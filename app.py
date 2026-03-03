"""
Financial Analyst AI - Streamlit Web Interface with Upload and Debug
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
    layout="wide"
)

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
        if len(chunk.split()) > 50:
            chunks.append(chunk)
    return chunks

def upload_document(text, ticker, doc_type="custom"):
    """Upload document to Pinecone with error handling"""
    
    # Chunk the text
    chunks = chunk_text(text)
    
    if not chunks:
        st.error("No chunks created! Text might be too short.")
        return 0
    
    st.info(f"Created {len(chunks)} chunks from document")
    
    index = pc.Index(INDEX_NAME)
    vectors = []
    uploaded_count = 0
    
    for i, chunk in enumerate(chunks):
        try:
            # Create embedding
            response = openai_client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small",
                dimensions=768
            )
            embedding = response.data[0].embedding
            
            # Prepare vector with unique ID
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
            st.warning(f"Error creating embedding for chunk {i}: {str(e)}")
            continue
    
    # Upload to Pinecone
    try:
        if vectors:
            index.upsert(vectors=vectors)
            uploaded_count = len(vectors)
            st.success(f"✓ Successfully uploaded {uploaded_count} vectors to Pinecone")
        else:
            st.error("No vectors to upload!")
            
    except Exception as e:
        st.error(f"Error uploading to Pinecone: {str(e)}")
        return 0
    
    return uploaded_count

# Header
st.title("📊 Financial Analyst AI Assistant")
st.markdown("Ask questions about SEC 10-K filings with AI-powered insights")

# Create tabs
tab1, tab2 = st.tabs(["💬 Ask Questions", "📤 Upload Documents"])

# ==================== TAB 1: ASK QUESTIONS ====================
with tab1:
    # Sidebar for filters
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
    st.subheader("Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Revenue Sources"):
            st.session_state.question = "What are the main revenue sources?"
    
    with col2:
        if st.button("⚠️ Risk Factors"):
            st.session_state.question = "What are the key risk factors?"
    
    with col3:
        if st.button("🤖 AI Strategy"):
            st.session_state.question = "How is the company investing in AI?"
    
    # Question input
    question = st.text_area(
        "Your question:",
        value=st.session_state.get('question', ''),
        height=100,
        placeholder="e.g., What were Microsoft's main growth drivers in 2024?"
    )
    
    # Search button
    if st.button("🔍 Get Answer", type="primary"):
        if not question:
            st.warning("Please enter a question!")
        else:
            with st.spinner("Searching documents and generating answer..."):
                
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
                index = pc.Index(INDEX_NAME)
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
                    st.error("No relevant documents found. Try adjusting your filters.")
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
                    st.success("✓ Answer generated!")
                    
                    st.markdown("---")
                    st.subheader("💡 Answer")
                    st.markdown(answer)
                    
                    st.markdown("---")
                    st.subheader("📚 Source Documents")
                    
                    for i, doc in enumerate(docs, 1):
                        with st.expander(f"Source {i}: {doc['ticker']} - {doc['section'].upper().replace('_', ' ')} (Relevance: {doc['score']:.2%})"):
                            st.markdown(doc['text'])

# ==================== TAB 2: UPLOAD DOCUMENTS ====================
with tab2:
    st.header("📤 Upload Your Own Documents")
    st.markdown("Upload text files, earnings reports, or other financial documents to analyze.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'html', 'htm', 'rtf'],
            help="Supported formats: .txt, .html, .htm, .rtf"
        )
    
    with col2:
        # Company ticker
        upload_ticker = st.text_input(
            "Company Ticker",
            placeholder="e.g., TSLA",
            max_chars=10
        ).upper()
        
        # Document type
        upload_doc_type = st.selectbox(
            "Document Type",
            ["Earnings Report", "Press Release", "Analyst Report", "Other"]
        )
    
    # Process upload
    if uploaded_file and upload_ticker:
        if st.button("📥 Process and Upload", type="primary"):
            with st.spinner("Processing document..."):
                
                st.write("**Debug Info:**")
                st.write(f"- File: {uploaded_file.name}")
                st.write(f"- Type: {uploaded_file.type}")
                st.write(f"- Size: {uploaded_file.size} bytes")
                
                # Read file
                try:
                    if uploaded_file.type == "text/plain":
                        text = uploaded_file.read().decode('utf-8')
                    elif 'rtf' in uploaded_file.type or uploaded_file.name.endswith('.rtf'):
                        # RTF file
                        content = uploaded_file.read().decode('utf-8', errors='ignore')
                        text = re.sub(r'\\[a-z]+\d*\s?', ' ', content)
                        text = re.sub(r'[{}]', '', text)
                        text = re.sub(r'\s+', ' ', text)
                    else:
                        # HTML file
                        html_content = uploaded_file.read().decode('utf-8')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text = soup.get_text(separator='\n')
                    
                    st.write(f"- Extracted text length: {len(text)} characters")
                    
                    # Clean
                    text = clean_text(text)
                    st.write(f"- After cleaning: {len(text)} characters")
                    
                    # Upload
                    num_chunks = upload_document(text, upload_ticker, upload_doc_type)
                    
                    if num_chunks > 0:
                        st.balloons()
                        st.success(f"✓ Document uploaded successfully!")
                        st.info(f"You can now search using ticker filter: {upload_ticker}")
                        
                        # Show preview
                        with st.expander("📄 Document Preview"):
                            st.text(text[:1000] + "..." if len(text) > 1000 else text)
                    else:
                        st.error("Upload failed - 0 chunks created")
                        
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # Show indexed documents
    st.markdown("---")
    st.subheader("📚 Indexed Documents")
    
    if st.button("🔄 Refresh Stats"):
        index = pc.Index(INDEX_NAME)
        stats = index.describe_index_stats()
        
        st.metric("Total Chunks in Database", stats['total_vector_count'])
        
        # DEBUG: Query to see what's there
        st.subheader("🔍 Sample Database Contents")
        
        results = index.query(
            vector=[0.1] * 768,
            top_k=10,
            include_metadata=True
        )
        
        # Group by ticker
        tickers_found = {}
        for match in results['matches']:
            ticker = match['metadata'].get('ticker', 'unknown')
            section = match['metadata'].get('section', 'unknown')
            
            if ticker not in tickers_found:
                tickers_found[ticker] = []
            tickers_found[ticker].append(section)
        
        # Display
        for ticker, sections in tickers_found.items():
            st.write(f"**{ticker}**: {len(sections)} chunks found")
            st.write(f"  Sections: {set(sections)}")
    
    # Test search
    st.markdown("---")
    st.subheader("🧪 Test Search")
    
    test_query = st.text_input("Test query:", "Tesla earnings")
    test_ticker = st.text_input("Filter by ticker:", "TSLA")
    
    if st.button("Test Search"):
        # Create embedding
        response = openai_client.embeddings.create(
            input=test_query,
            model="text-embedding-3-small",
            dimensions=768
        )
        query_embedding = response.data[0].embedding
        
        # Search with filter
        index = pc.Index(INDEX_NAME)
        results = index.query(
            vector=query_embedding,
            top_k=5,
            include_metadata=True,
            filter={'ticker': test_ticker} if test_ticker else None
        )
        
        st.write(f"Found {len(results['matches'])} results")
        
        for i, match in enumerate(results['matches'], 1):
            st.write(f"{i}. Score: {match['score']:.3f}")
            st.write(f"   Ticker: {match['metadata'].get('ticker')}")
            st.write(f"   Section: {match['metadata'].get('section')}")
            st.write(f"   Text: {match['metadata'].get('text')[:100]}...")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 About")
st.sidebar.info("""
**Financial Analyst AI**

Ask questions about SEC filings and get AI-powered answers with citations.

Built with:
- Claude API (Anthropic)
- OpenAI Embeddings
- Pinecone Vector DB
""")