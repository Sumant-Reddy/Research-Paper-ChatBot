from langchain_core.documents import Document

def json_to_documents(json_data):
    docs = []
    for section in json_data["sections"]:
        if len(section["content"].strip()) > 30:
            docs.append(Document(
                page_content=section["content"],
                metadata={"section": section["section_title"], "source": json_data.get("title")}
            ))
    return docs
