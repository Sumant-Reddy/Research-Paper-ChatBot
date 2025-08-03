from langchain.memory import ConversationBufferMemory

def get_chat_memory():
    # Use the latest recommended arguments for ConversationBufferMemory
    return ConversationBufferMemory()
