from langchain_core.prompts import PromptTemplate

def get_persona_prompt(persona="default"):
    system_instruction = {
        "default": "You are a helpful assistant answering questions about scientific papers.",
        "professor": "You are a senior researcher summarizing complex papers for junior students.",
        "student": "You are a student trying to understand the main idea and method."
    }.get(persona, "default")

    return PromptTemplate.from_template(f"""
{system_instruction}

<context>
{{context}}
</context>

Question: {{input}}
Answer:""")
