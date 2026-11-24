from pathlib import Path
from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from prompts import RAG_PROMPT

load_dotenv()

DATA_DIR = Path('data/documents')




def ask_question(question):
    llm = ChatGroq(model="openai/gpt-oss-120b")
    response = llm.invoke(question)
    return response.content

def build_store():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    store = InMemoryVectorStore(embeddings)

    docs, metadata = [], []
    for path in sorted(DATA_DIR.glob("*.md")):
        docs.append(path.read_text())
        metadata.append({'source': path.name})

    store.add_texts(docs, metadata=metadata)
    return store, len(docs), metadata

def ask_rag(store, question, k=3):
    results = store.similarity_search_with_score(question, k=k)
    # for doc, score in results:
    #     print(f"score={score:.3f} source={doc.metadata}")

    context = "\n\n---\n\n".join(doc.page_content for doc, _ in results)
    prompt = RAG_PROMPT.format(retrieved_context=context, user_question=question)

    return ask_question(prompt)