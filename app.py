import streamlit as st
import os
import sys

# Add root directory to path (ensures imports work)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import modules from ingestion and rag
from ingestion.extractor import parse_pdf_to_json
from ingestion.chunker import json_to_documents
from ingestion.arxiv_fetcher import download_latest_papers
from rag.vector_store import create_or_load_vectorstore
from rag.chain import build_rag_chain
from dotenv import load_dotenv

load_dotenv()

# Streamlit UI setup
st.set_page_config(page_title="📄 Research Paper QA Assistant", layout="wide")
st.title("📄 Research Paper QA Assistant")

mode = st.radio("Choose source:", ["📁 Upload PDF", "🌐 ArXiv Search"])

selected_path = None

if mode == "📁 Upload PDF":
    pdf_file = st.file_uploader("Upload a paper (PDF)", type="pdf")
    if pdf_file:
        os.makedirs("data/papers", exist_ok=True)
        temp_path = os.path.join("data/papers", pdf_file.name)
        with open(temp_path, "wb") as f:
            f.write(pdf_file.read())
        selected_path = temp_path

elif mode == "🌐 ArXiv Search":
    query = st.text_input("Search topic:")
    if st.button("Fetch from ArXiv"):
        paths = download_latest_papers(query)
        if paths:
            selected_path = paths[0]
            st.success(f"Downloaded: {os.path.basename(selected_path)}")
        else:
            st.error("No papers found.")

question = st.text_input("Ask a question:")
persona = st.selectbox("Select persona", ["default", "student", "professor"])

if st.button("Run QA") and selected_path:
    with st.spinner("Processing..."):
        paper_json = parse_pdf_to_json(selected_path)
        print("✅ JSON keys:", paper_json.keys())
        print("✅ JSON content sample:", str(paper_json)[:500])
        docs = json_to_documents(paper_json)
        print(f"Loaded {len(docs)} documents.")
        for d in docs:
            print(f"- [{len(d.page_content)} chars] {d.metadata.get('source', '')}")
        vectordb = create_or_load_vectorstore(docs)
        chain = build_rag_chain(vectordb, persona)

        response = chain.invoke(question)
        st.subheader("💬 Answer")
        st.markdown(response.content)
