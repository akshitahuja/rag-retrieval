from pathlib import Path
from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from prompts import RAG_PROMPT

load_dotenv()

DATA_DIR = Path('data/documents')




def ask_question(question):
    llm = ChatGroq(model="openai/gpt-oss-120b")
    response = llm.invoke(question)
    return response.content

def build_in_memory_store():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    store = InMemoryVectorStore(embeddings)

    docs, metadata = [], []
    for path in sorted(DATA_DIR.glob("*.md")):
        docs.append(path.read_text())
        metadata.append({'source': path.name})

    store.add_texts(docs, metadata=metadata)
    return store, len(docs), metadata

def build_in_memory_store_with_chunking():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    store = InMemoryVectorStore(embeddings)

    all_chunks, _ = markdown_chunks()
    store.add_documents(documents=all_chunks)

    return store, len(all_chunks), []

def build_chrome_store_with_chunking():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    store = Chroma(
        collection_name="it_support_docs",
        embedding_function=embeddings,
        persist_directory="./chroma_db",  # Saves automatically to disk
    )

    return store
    
def sync_add_docs(store):
    all_chunks, all_ids = markdown_chunks()
    # 4. Upsert documents (adds new chunks and updates existing IDs)
    store.add_documents(documents=all_chunks, ids=all_ids)

    return store, len(all_chunks), []

def markdown_chunks():
    # 1. Split on headers to preserve document hierarchy in metadata
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,  # Keeps the header text inside the chunk content as well
    )
    
    all_chunks = []
    all_ids = []
    for path in sorted(DATA_DIR.glob("*.md")):
        md_splits = markdown_splitter.split_text(path.read_text())

        for doc in md_splits:
            doc.metadata["source"] = str(path)
            doc.metadata["filename"] = path.name

        for idx, chunk in enumerate(md_splits):
            all_chunks.append(chunk)
            all_ids.append(f"{str(path)}::chunk_{idx}")

    return all_chunks, all_ids

    # 2. Recursively split large sections while respecting code blocks and paragraphs
    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=1000,
    #     chunk_overlap=150,
    # )
    # final_chunks = text_splitter.split_documents(md_header_splits)

def ask_rag(store, question, k=3):
    results = store.similarity_search_with_score(question, k=k)
    # for doc, score in results:
    #     print(f"score={score:.3f} source={doc.metadata}")

    context = "\n\n---\n\n".join(doc.page_content for doc, _ in results)
    prompt = RAG_PROMPT.format(retrieved_context=context, user_question=question)

    return ask_question(prompt)
