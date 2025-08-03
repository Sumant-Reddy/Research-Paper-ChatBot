import streamlit as st
import os
import sys
import base64
from io import BytesIO

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

# --- Custom CSS for robust color themes, font, and centered title ---
CUSTOM_THEMES = {
    "Classic": {
        "background": "#f8f9fa",
        "font": "'Segoe UI', Arial, sans-serif",
        "color": "#222"
    },
    "Ocean": {
        "background": "linear-gradient(135deg, #43cea2 0%, #185a9d 100%)",
        "font": "'Segoe UI', Arial, sans-serif",
        "color": "#fff"
    },
    "Sunset": {
        "background": "linear-gradient(135deg, #ff9966 0%, #ff5e62 100%)",
        "font": "'Segoe UI', Arial, sans-serif",
        "color": "#fff"
    },
    "Dark": {
        "background": "#222",
        "font": "'Segoe UI', Arial, sans-serif",
        "color": "#eee"
    }
}

PERSONA_COLORS = {
    "default": "#e3f2fd",
    "student": "#fff9c4",
    "professor": "#ffe0b2"
}

# Theme selection
st.set_page_config(page_title="Research Paper QA Assistant", layout="wide")

# --- Sidebar for global controls ---
st.sidebar.title("📄 Research Paper QA Assistant")
mode = st.sidebar.radio("Choose source:", ["📁 Upload PDFs", "🌐 ArXiv Search"])
persona = st.sidebar.selectbox("Select persona", ["default", "student", "professor"])
question = st.sidebar.text_input("Ask a question:")
# --- Theme Selector below 'Ask a Question' ---
st.markdown("<div style='height:0.5em;'></div>", unsafe_allow_html=True)
theme = st.selectbox(
    "Theme",
    list(CUSTOM_THEMES.keys()),
    index=0,
    key="theme_selectbox",
    help="Change the color theme of the app.",
)
# --- Fixed Top Bar with Project Name (centered, always full width) ---
st.markdown(f'''
    <style>
    .fixed-top-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        z-index: 9999;
        background: rgba(255,255,255,0.97);
        border-bottom: 2px solid #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        height: 60px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        pointer-events: none;
    }}
    .fixed-top-bar-title {{
        text-align: right;
        font-size: 2.2em;
        font-weight: bold;
        letter-spacing: 1px;
        color: #185a9d;
        font-family: 'Segoe UI', Arial, sans-serif;
        margin: 0 2vw 0 0;
        padding-left: 2vw;
        padding-right: 2vw;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        display: flex;
        align-items: center;
        height: 60px;
        z-index: 10000;
        pointer-events: auto;
    }}
    .stApp {{padding-top: 70px !important;}}
    @media (max-width: 900px) {{
        .fixed-top-bar-title {{
            font-size: 1.3em;
        }}
    }}
    /* Make columns and main container use full width in wide/fullscreen mode */
    section.main > div.block-container {{
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100vw !important;
        width: 100vw !important;
    }}
    .element-container, .stColumn {{
        width: 100% !important;
        max-width: 100vw !important;
    }}
    /* Responsive sidebar: when open, main content shrinks accordingly */
    [data-testid="stSidebar"] ~ section.main {{
        margin-left: 0 !important;
        width: 100vw !important;
        transition: margin-left 0.2s, width 0.2s;
    }}
    [data-testid="stSidebar"][aria-expanded="true"] ~ section.main {{
        margin-left: 20rem !important; /* Sidebar width */
        width: calc(100vw - 20rem) !important;
    }}
    /* Make preview/table boxes use full width */
    .stTable, .pdf-preview, .persona-answer {{
        width: 100% !important;
        max-width: 100vw !important;
        box-sizing: border-box !important;
    }}
    .stButton>button {{
        font-weight: bold !important;
        font-size: 1.1em !important;
        color: #222 !important;
        background: #e3f2fd !important;
        border-radius: 6px !important;
        border: 1.5px solid #185a9d !important;
        transition: background 0.2s, color 0.2s;
    }}
    .stButton>button:hover {{
        color: #fff !important;
        background: #185a9d !important;
    }}
    .pdf-preview {{
        margin-bottom: 0.5em;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 0.5em;
        background: #fafafa;
        min-width: 180px;
        max-width: 600px;
        width: fit-content;
        color: {CUSTOM_THEMES[theme]['color']};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 1em;
        word-break: break-word;
    }}
    /* Uniform gap for question area */
    .qa-section-header {{ margin-bottom: 2.2em !important; }}
    .qa-label {{ margin-bottom: 1.2em !important; display:block; }}
    .qa-btn {{ margin-top: 1.2em !important; margin-bottom: 1.2em !important; }}
    </style>
    <div class="fixed-top-bar">
        <span class="fixed-top-bar-title">PaperBot: Research Paper QA Assistant</span>
    </div>
''', unsafe_allow_html=True)

# --- Theme Selector in Top Bar (not sidebar) ---
# Move the selectbox to the right in the top bar using JS
st.markdown('''<script>
var anchor = window.parent.document.getElementById('theme-dropdown-anchor');
var themeBox = window.parent.document.querySelector('label[for="theme_selectbox"]')?.parentElement;
if (anchor && themeBox) { anchor.appendChild(themeBox); }
</script>''', unsafe_allow_html=True)

# Robust CSS for full-app theming
css = f"""
    <style>
    .stApp {{
        background: {CUSTOM_THEMES[theme]['background']} !important;
        background-color: {CUSTOM_THEMES[theme]['background']} !important;
        color: {CUSTOM_THEMES[theme]['color']} !important;
        font-family: {CUSTOM_THEMES[theme]['font']} !important;
        min-height: 100vh !important;
    }}
    html, body {{
        background: {CUSTOM_THEMES[theme]['background']} !important;
        background-color: {CUSTOM_THEMES[theme]['background']} !important;
        color: {CUSTOM_THEMES[theme]['color']} !important;
        font-family: {CUSTOM_THEMES[theme]['font']} !important;
        min-height: 100vh !important;
    }}
    .stButton>button {{margin-top: 0.5em; margin-bottom: 0.5em;}}
    .stSelectbox, .stTextInput, .stNumberInput {{margin-bottom: 1em;}}
    .stExpanderHeader {{font-weight: bold; color: #2c3e50;}}
    .stTable {{background: #fff; border-radius: 8px;}}
    .pdf-download {{margin-top: 0.2em; margin-bottom: 0.2em;}}
    .pdf-preview {{margin-bottom: 0.5em; border: 1px solid #ddd; border-radius: 6px; padding: 0.5em; background: #fafafa;}}
    .center-title {{text-align: center; font-size: 2.2em; font-weight: bold; margin-bottom: 0.5em; letter-spacing: 1px;}}
    .persona-answer {{border-radius: 8px; padding: 1em; margin-top: 1em; font-size: 1.1em;}}
    </style>
"""
st.markdown(css, unsafe_allow_html=True)


# Initialize session state for selected_paths
if "selected_paths" not in st.session_state:
    st.session_state.selected_paths = []
if "arxiv_mode" not in st.session_state:
    st.session_state.arxiv_mode = False

# --- Main layout header: 1 and 2 side by side ---
st.markdown(
    """
    <div style='margin-bottom: 0.5em;'>
        <span style='font-size:1.3em; font-weight:600;'>1. Select or Fetch Papers</span>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([2, 3], gap="large")

with col1:
    if mode == "📁 Upload PDFs":
        st.session_state.arxiv_mode = False
        num_pdfs = st.number_input("How many PDFs do you want to upload?", min_value=1, max_value=10, value=1, step=1)
        st.markdown("<div style='margin-bottom:0.5em;'>Drag and drop your PDFs below:</div>", unsafe_allow_html=True)
        pdf_files = st.file_uploader("Upload papers (PDF)", type="pdf", accept_multiple_files=True)
        if pdf_files:
            os.makedirs("data/papers", exist_ok=True)
            paths = []
            for pdf_file in pdf_files[:num_pdfs]:
                temp_path = os.path.join("data/papers", pdf_file.name)
                with open(temp_path, "wb") as f:
                    f.write(pdf_file.read())
                paths.append(temp_path)
            st.session_state.selected_paths = paths
            st.success(f"Uploaded: {', '.join([os.path.basename(p) for p in paths])}")
    elif mode == "🌐 ArXiv Search":
        st.session_state.arxiv_mode = True
        query = st.text_input("Search topic:")
        num_arxiv = st.number_input("How many relevant papers to fetch?", min_value=1, max_value=10, value=1, step=1)
        if st.button("Fetch from ArXiv"):
            paths = download_latest_papers(query, max_results=num_arxiv)
            if paths:
                st.session_state.selected_paths = paths
                st.success(f"Downloaded: {', '.join([os.path.basename(p) for p in paths])}")
            else:
                st.error("No papers found.")
    # Show summary table of selected papers and download buttons for ArXiv
    selected_paths = st.session_state.selected_paths
    if selected_paths:
        st.markdown("#### Selected Papers")
        paper_names = [os.path.basename(p) for p in selected_paths]
        # 1-based indexing for file numbering
        numbered_names = [f"{i+1}. {name}" for i, name in enumerate(paper_names)]
        if st.session_state.arxiv_mode:
            for p, name in zip(selected_paths, numbered_names):
                with open(p, "rb") as f:
                    pdf_bytes = f.read()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{name}" class="pdf-download">⬇️ Download {name}</a>'
                st.markdown(href, unsafe_allow_html=True)
        st.table({"File Name": numbered_names})

        # --- PDF preview with slider and neutral color box ---
        st.markdown("<b>Preview Papers</b>", unsafe_allow_html=True)
        if len(selected_paths) > 1:
            preview_index = st.slider(
                "Select paper to preview",
                min_value=1,
                max_value=len(selected_paths),
                value=1,
                format="%d"
            ) - 1  # 1-based to 0-based
        else:
            preview_index = 0

        p = selected_paths[preview_index]
        name = numbered_names[preview_index]
        try:
            import pdfplumber
            with pdfplumber.open(p) as pdf:
                first_page = pdf.pages[0].extract_text() if pdf.pages else "(No pages)"
            preview = first_page[:800] + ("..." if first_page and len(first_page) > 800 else "") if first_page else "(No extractable text)"
        except Exception:
            preview = "(Preview unavailable)"
        st.markdown(
            f"""
            <div style='
                margin-bottom:1em;
                border: 1.5px solid #bbb;
                border-radius: 8px;
                padding: 1em;
                background: #f4f4f4;
                color: #222;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 1.05em;
                word-break: break-word;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            '>
                <b>{name}</b><br>
                <pre style='white-space:pre-wrap; font-family: "Segoe UI", Arial, monospace; background: none; color: #333;'>{preview}</pre>
            </div>
            """,
            unsafe_allow_html=True
        )

with col2:
    # Add the header above the question input
    st.markdown(
        """
        <div class='qa-section-header' style='margin-bottom: 2.2em;'>
            <span style='font-size:1.3em; font-weight:600;'>2. Ask a Question & Select Sections</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Center the first question input and run button
    st.markdown(
        """
        <div style='display: flex; flex-direction: column; align-items: center;'>
            <div style='width: 100%; max-width: 500px;'>
                <label class='qa-label' style='font-size:1.1em; font-weight:500;'>Ask a question:</label>
        """, unsafe_allow_html=True
    )
    question1 = st.text_input("Question 1", value=question, key="centered_question_input", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    run_qa1 = st.button("Run QA", key="run_qa_btn", help="Click to run QA on selected sections", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

    # Output for first question
    if run_qa1 and st.session_state.selected_paths:
        with st.spinner("Processing all selected papers..."):
            all_sections = []
            extraction_methods = set()
            titles = []
            for path in st.session_state.selected_paths:
                paper_json = parse_pdf_to_json(path)
                extraction_method = paper_json.get("extraction_method", "unknown")
                extraction_methods.add(extraction_method)
                sections = paper_json.get("sections", [])
                title = paper_json.get("title", os.path.basename(path))
                titles.append(title)
                # Tag each section with its source
                for s in sections:
                    s["source"] = title
                all_sections.extend(sections)
            st.info(f"Extraction methods used: {', '.join(extraction_methods)}")
            if not all_sections or all(len(s["content"].strip()) <= 30 for s in all_sections):
                st.error("No extractable text found in the selected PDFs. Try other files or methods.")
            else:
                # Section selection with index (no hover preview)
                section_titles = [f"{i+1}. {s['section_title']} ({len(s['content'])} chars) [{s['source']}]" for i, s in enumerate(all_sections)]
                # For the multiselect, use the indexed section_titles as options
                selected_sections = st.multiselect(
                    "Choose sections:",
                    options=section_titles,
                    default=section_titles,
                    key="section_multiselect"
                )
                selected_docs = [s for s, t in zip(all_sections, section_titles) if t in selected_sections and len(s["content"].strip()) > 30]
                if not selected_docs:
                    st.warning("No sections selected or all are too short.")
                else:
                    from langchain_core.documents import Document
                    docs = [Document(
                        page_content=s["content"],
                        metadata={"section": s["section_title"], "source": s["source"]}
                    ) for s in selected_docs]
                    vectordb = create_or_load_vectorstore(docs)
                    chain = build_rag_chain(vectordb, persona)
                    response = chain.invoke(question1)
                    persona_label = persona.capitalize() if persona != "default" else "Assistant"
                    answer_color = PERSONA_COLORS.get(persona, "#e3f2fd")
                    st.markdown(f'<div class="persona-answer" style="background:{answer_color}; border:1.5px solid #bbb;"><b>{persona_label} Answer:</b><br>{response.content}</div>', unsafe_allow_html=True)
    
        # Now show the second question input and run button below the first answer
        st.markdown(
            """
            <div style='display: flex; flex-direction: column; align-items: center; margin-top: 2em; margin-bottom: 2em;'>
                <div style='width: 100%; max-width: 500px;'>
                    <label class='qa-label' style='font-size:1.1em; font-weight:500;'>Ask another question:</label>
            """, unsafe_allow_html=True
        )
        question2 = st.text_input("Question 2", key="second_question_input", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        run_qa2 = st.button("Run QA for Question 2", key="run_qa_btn2", help="Click to run QA on selected sections", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

        # Output for second question
        if run_qa2:
            with st.spinner("Processing all selected papers for second question..."):
                all_sections = []
                extraction_methods = set()
                titles = []
                for path in st.session_state.selected_paths:
                    paper_json = parse_pdf_to_json(path)
                    extraction_method = paper_json.get("extraction_method", "unknown")
                    extraction_methods.add(extraction_method)
                    sections = paper_json.get("sections", [])
                    title = paper_json.get("title", os.path.basename(path))
                    titles.append(title)
                    # Tag each section with its source
                    for s in sections:
                        s["source"] = title
                    all_sections.extend(sections)
                st.info(f"Extraction methods used: {', '.join(extraction_methods)}")
                if not all_sections or all(len(s["content"].strip()) <= 30 for s in all_sections):
                    st.error("No extractable text found in the selected PDFs. Try other files or methods.")
                else:
                    # Section selection with index (no hover preview)
                    section_titles = [f"{i+1}. {s['section_title']} ({len(s['content'])} chars) [{s['source']}]" for i, s in enumerate(all_sections)]
                    # For the multiselect, use the indexed section_titles as options
                    selected_sections = st.multiselect(
                        "Choose sections for second question:",
                        options=section_titles,
                        default=section_titles,
                        key="section_multiselect2"
                    )
                    selected_docs = [s for s, t in zip(all_sections, section_titles) if t in selected_sections and len(s["content"].strip()) > 30]
                    if not selected_docs:
                        st.warning("No sections selected or all are too short for the second question.")
                    else:
                        from langchain_core.documents import Document
                        docs = [Document(
                            page_content=s["content"],
                            metadata={"section": s["section_title"], "source": s["source"]}
                        ) for s in selected_docs]
                        vectordb = create_or_load_vectorstore(docs)
                        chain = build_rag_chain(vectordb, persona)
                        response = chain.invoke(question2)
                        persona_label = persona.capitalize() if persona != "default" else "Assistant"
                        answer_color = PERSONA_COLORS.get(persona, "#e3f2fd")
                        st.markdown(f'<div class="persona-answer" style="background:{answer_color}; border:1.5px solid #bbb;"><b>{persona_label} Answer 2:</b><br>{response.content}</div>', unsafe_allow_html=True)
