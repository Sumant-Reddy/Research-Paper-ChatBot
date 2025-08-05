# 🤖 PaperBot: Research Paper QA Assistant

A modern, interactive Streamlit application for exploring and questioning research papers (PDFs or ArXiv) using **RAG (Retrieval-Augmented Generation)**, **LangChain**, **ChromaDB**, and **Google Generative AI embeddings**.

---

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-RAG-yellow)

---

## 🚀 Live Demo

Try it now → [**https://research-paper-chatbot.streamlit.app/**](https://paperbot.streamlit.app/)

---

## ✨ Key Features

- 📄 Upload your own research PDFs or fetch directly from **ArXiv**
- 🔍 Preview, select, and download relevant papers
- ❓ Ask contextual questions from selected documents
- 🧠 Persona-based QA modes: *Student*, *Professor*, *General*
- 📎 Section-level chunking for focused answers
- 🧾 Chroma vector store with persistent storage
- 🎨 Responsive Streamlit UI with light/dark mode

---

## 🧱 Tech Stack

- **Frontend**: Streamlit  
- **RAG Backbone**: LangChain  
- **Vector DB**: ChromaDB (`persist_directory`)  
- **Embeddings**: Google Generative AI (`models/embedding-001`)  
- **PDF + ArXiv**: `PyMuPDF`, `arxiv` API  
- **Memory**: `ConversationBufferMemory` for chat history  
- **Prompting**: Persona-based LangChain templates  

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Sumant-Reddy/Research-Paper-ChatBot.git
cd Research-Paper-ChatBot

2. Create a Virtual Environment
Copy
Edit
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

3. Install Dependencies
Copy
Edit
pip install -r requirements.txt

4. Add Google API Key
Create a .env file in the project root with:
ini
Copy
Edit
GOOGLE_API_KEY=your-google-api-key

5. Run the App
bash
Copy
Edit
streamlit run app.py
The app will launch at: http://localhost:8501

🗂️ Project Structure
graphql
Copy
Edit
📁 Research-Paper-ChatBot/
├── app.py                  # Streamlit UI and app logic
├── requirements.txt        # All Python dependencies
├── .env                    # Your Google API key
├── README.md               # You're reading it!
│
├── ingestion/              # PDF parsing & ArXiv fetching
│   └── extractor.py
│
├── rag/                    # Embedding & RAG chain logic
│   ├── vector_store.py
│   └── rag_chain.py
│
├── utils/                  # Prompt templates, helper functions
│   └── prompts.py
│
└── data/                   # Uploaded PDFs and Chroma DB

💡 How It Works
Ingestion: Load PDFs or fetch from ArXiv using the arxiv API

Parsing: PDFs are chunked by section/page with metadata

Embedding: Text chunks are embedded using Google GenAI

Retrieval: ChromaDB returns most relevant chunks via similarity search

Answering: LangChain + prompt template generates an answer (persona-based)

🧑‍🏫 Usage Tips
👨‍🎓 Choose personas for tailored responses (student, professor, etc.)

🧠 Ask high-level or section-specific questions

📁 Select multiple papers to create a unified context

🌐 Deployment (Optional)
Deploy on Streamlit Cloud:

Push the repo to GitHub

Go to Streamlit Cloud

Link the GitHub repo and set app.py as the entrypoint

Add your GOOGLE_API_KEY as a secret in App Settings → Secrets

🐞 Troubleshooting
Problem	Fix
ChromaDB/SQLite errors	Ensure pysqlite3-binary is installed
Embedding fails	Check .env for valid GOOGLE_API_KEY
PDF parsing issues	Try uploading better quality PDFs (text-based, not image scanned)
App crashes on multiple PDFs	Restart app or check for missing text extraction in PDFs

📄 License
This project is licensed under the MIT License.

🙌 Contributions
Contributions and feedback are welcome!
Open an issue or submit a pull request 🚀

🧠 Author
Developed by Sumanth Reddy
⭐️ If you found this useful, please star the repo! in this make the file structure as separate from bash
