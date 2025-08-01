from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableMap, RunnablePassthrough
from utils.prompts import get_persona_prompt
from rag.memory import get_chat_memory

def build_rag_chain(vectordb, persona="default"):
    retriever = vectordb.as_retriever(search_type="mmr", k=4)
    prompt = get_persona_prompt(persona)
    memory = get_chat_memory()

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        temperature=0.4,
        streaming=True
    )

    chain = RunnableMap({
        "context": retriever,
        "input": RunnablePassthrough()
    }) | prompt | llm

    return chain
