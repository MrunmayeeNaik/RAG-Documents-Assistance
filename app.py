import os
import tempfile

import streamlit as st
import pymupdf
from pypdf import PdfReader  #usinng pypdf to read and parse pdf files
import pandas as pd           #to read excel files

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from streamlit.runtime.uploaded_file_manager import UploadedFile

from chat import generate_answer

def process_document(uploaded_file:UploadedFile) -> list[Document]:
    file_extensions ='.pdf'
    temp_file =tempfile.NamedTemporaryFile("wb",suffix=file_extensions,delete=False)
    temp_file.write(uploaded_file.read())
    loader =PyMuPDFLoader(temp_file.name)
    docs=loader.load()
    docs.close()
    os.unlink(temp_file.name)

    text_splitter =RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=["\n\n","",".","?","!", ""," "]
    )
    return text_splitter.split_documents(docs)


if __name__ == "__main__":
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload your file here", type=["pdf","xls"], accept_multiple_files=False)
        process=st.button("Process",)

    if uploaded_file and process:  
        all_splits=process_document(uploaded_file)
        st.write(all_splits)


    





