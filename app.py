import os
import tempfile

import streamlit as st
import pymupdf
from pypdf import PdfReader  #usinng pypdf to read and parse pdf files
import pandas as pd           #to read excel files
import ollama
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from streamlit.runtime.uploaded_file_manager import UploadedFile

import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

system_prompt = """"
You are an expert AI assistant tasked with providing detailed answers solely based on the given content. Your main goal is to analyze
the information provided and formulate a comprehensive, well-structured response to the question.

context will be passed as "Context:"
user question will be passed as  "Question:"

To answer the question :
1.Thoroughly analyze the context, identifying key information relevant to the question.
2. Organize your thoughts and plan your response to ensure a logical flow of information.
3. Formulate a detailed answer that directly addresses the question, using only the information provided in the context.
4. Ensure your answer is comprehensive, covering all relevant aspects found in the context.
5. If the context doesn't contain sufficient information to fully answer the question, state this clearly in your response.

Format your response as follows:
1. Use clear, concise language.
2. Organize your answer into paragraphs for readability.
3. Use bullet points or numbered lists where appropriate to break down complex information.
4. If relevant, include any headings or subheadings to structure your response.
5. Ensure proper grammar, punctuation, and spelling throughout your answer.

Important: Base your entire response solely on the information provided in the context. Do not include any external knowledge or assumptions not present in the given text.
"""


def process_document(uploaded_file: UploadedFile) -> list[Document]:
    data = uploaded_file.read()
    if not data:
        raise ValueError("The file is empty. Please upload a file with content.")

    file_extensions = ".pdf"
    with tempfile.NamedTemporaryFile("wb", suffix=file_extensions, delete=False) as temp_file:
        temp_file.write(data)
        temp_path = temp_file.name

    try:
        try:
            loader = PyMuPDFLoader(temp_path)
            docs = loader.load()
        except Exception:
            raise ValueError(
                "The file could not be read. It may be corrupted or in an unsupported format."
            ) from None

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
            separators=["\n\n", "", ".", "?", "!", "", " "],
        )
        return text_splitter.split_documents(docs)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Function for Vector Database
def get_vector_collection() ->chromadb.Collection:
    ollama_ef=OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text:latest",
    )

    chroma_client=chromadb.PersistentClient(path="./demo-rag-chroma")
    return chroma_client.get_or_create_collection(
        name = "rag_app",
        embedding_function=ollama_ef,
        metadata={"hnsw:space":"cosine"},
    )

#function to store document in vector collection
def add_to_vector_collection(all_splits:list[Document],file_name:str):
    if not all_splits:
        st.error("No text could be extracted from this document. Ensure it's a valid PDF with readable (selectable) text.")
        return

    collection = get_vector_collection()
    documents, metadatas, ids = [], [], []

    for idx, split in enumerate(all_splits):
        if split.page_content.strip():  # skip empty chunks
            documents.append(split.page_content)
            metadatas.append(split.metadata)
            ids.append(f"{file_name}_{idx}")

    if not documents:
        st.error("No text could be extracted from this document. The PDF may be image-only (scanned) or empty.")
        return

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    st.success("Data Added to vector store")

# function to answer user prompt
def query_collection(prompt:str ,n_results:int=10):
    collection = get_vector_collection()
    results = collection.query(query_texts=[prompt],n_results=n_results)
    return results

#function to call the LLM 
def call_llm(context:str, prompt:str):
    response = ollama.chat(
        model ="llama3.2",
        stream=True,
        messages = [
            {
                "role":"system",
                "content":system_prompt,
            },
            {
                "role":"user",
                "content":f"Context: {context},Question:{prompt}",
            },
        ],
    )
    for chunk in response:
        if chunk.get("message", {}).get("content"):
            yield chunk["message"]["content"]
        if chunk.get("done"):
            break


#Streamlit App
if __name__ == "__main__":
    st.title("RAG Q&A App 🧠")

    uploaded_file = st.sidebar.file_uploader("Upload your file here", type=["pdf", "xls"])
    process = st.sidebar.button("Process")

    if uploaded_file is not None:
        st.sidebar.write("📄 File uploaded:", uploaded_file.name)

    if uploaded_file and process:
        normalize_uploaded_file_name = uploaded_file.name.translate(
            str.maketrans({"-": "_", ".": "_"})
        )
        try:
            all_splits = process_document(uploaded_file)
            add_to_vector_collection(all_splits, normalize_uploaded_file_name)
        except ValueError as e:
            st.error(str(e))
    elif process and not uploaded_file:
        st.error("Please upload a file")

    prompt=st.text_area("*Ask a question related to your document:*")
    ask=st.button("Ask")

    if ask and prompt:
        try:
            results = query_collection(prompt)
            docs = results.get("documents") or []
            if not docs or not docs[0]:
                st.warning("No relevant context found. Make sure you've processed a document first.")
            else:
                context = "\n\n".join(docs[0])  # join chunks into single string
                response = call_llm(context=context, prompt=prompt)
                st.write_stream(response)
        except Exception as e:
            st.error(f"Error generating response: {e}")

    