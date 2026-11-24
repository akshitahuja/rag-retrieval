import streamlit as st

from rag import build_store, ask_rag

st.set_page_config(page_title="Internal Docs RAG", layout="wide")
st.title("📄 Internal Knowledge Assistant")

# 1. Sidebar for document ingestion
with st.sidebar:
    st.header("Knowledge Base")
    button = st.button("Process Documents")
    if button:
        with st.spinner("Chunking and indexing documents..."):
            store, total_docs, metadata = build_store()
            st.session_state.store = store
            st.session_state.vector_db_ready = True
            st.success(f"Indexed {total_docs} files!")
    # uploaded_files = st.file_uploader(
    #     "Upload internal PDFs or TXT files",
    #     type=["pdf", "txt"],
    #     accept_multiple_files=True,
    # )
    # if uploaded_files and st.button("Process Documents"):
    #     with st.spinner("Chunking and indexing documents..."):
    #         # Replace with your vector store logic (e.g., FAISS, Chroma, Qdrant)
    #         st.session_state.vector_db_ready = True
    #         st.success(f"Indexed {len(uploaded_files)} files!")

# 2. Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Upload your docs on the left and ask me anything!"}
    ]

# 3. Render existing messages
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])
#         if "sources" in msg:
#             with st.expander("View Sources"):
#                 st.write(msg["sources"])

# 4. Handle new user prompt
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):
        if not st.session_state.get("vector_db_ready"):
            reply = "Please upload and process at least one document first."
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            with st.spinner("Searching internal docs..."):
                # Replace with actual retriever + LLM call
                response = ask_rag(st.session_state.store, prompt)
                # reply = f"Based on your documents, here is the answer\n{response}"

                reply = (
                    # f"Based on your documents, here is the answer:\n"
                    f"{response}"
                )

                # sources = ["policy_manual.pdf (Page 4)", "onboarding_guide.txt"]

                st.markdown(reply)
                # with st.expander("View Sources"):
                #     st.write(sources)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    # "sources": sources
                })
