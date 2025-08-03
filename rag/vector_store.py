import os
import asyncio
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_or_load_vectorstore(documents):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    # Filter out empty documents
    non_empty_docs = [doc for doc in documents if doc.page_content.strip()]
    if not non_empty_docs:
        raise ValueError("No non-empty documents to index.")

    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    vectorstore = Chroma.from_documents(
        non_empty_docs,
        embedding=embedding,
        persist_directory="data/chroma_db"
    )
    return vectorstore

