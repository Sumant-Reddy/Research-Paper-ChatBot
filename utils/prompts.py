from langchain_core.prompts import PromptTemplate

def get_persona_prompt(persona="default"):
    if persona == "professor":
        system_instruction = (
            "You are a senior researcher (professor) answering questions about scientific papers. "
            "Provide a detailed, technical, and structured answer. Use numbered points or sections if relevant. "
            "Explain advanced concepts clearly, and include references to the context when possible."
        )
    elif persona == "student":
        system_instruction = (
            "You are a student trying to understand the main idea and method of a scientific paper. "
            "Answer in a simple, step-by-step, and easy-to-understand way. Use numbered lists or bullet points. "
            "Focus on the main idea, method, and key results. Avoid jargon."
        )
    else:
        system_instruction = (
            "You are a helpful AI assistant answering questions about scientific papers. "
            "Be concise, clear, and informative. Use numbers or bullet points if it helps clarity."
        )

    return PromptTemplate.from_template(f"""
{system_instruction}

<context>
{{context}}
</context>

Question: {{input}}
Answer:
""")
