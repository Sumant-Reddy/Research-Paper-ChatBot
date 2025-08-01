from langchain.memory import ConversationBufferMemory

def get_chat_memory():
    return ConversationBufferMemory(return_messages=True)
