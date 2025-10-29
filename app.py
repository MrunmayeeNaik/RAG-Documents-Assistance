import streamlit as st
import pymupdf
from pypdf import PdfReader  #usinng pypdf to read and parse pdf files
#from openpyxl import load_workbook  using openpyxl to read and parse excel files
import pandas as pd           #to read excel files

from chat import generate_answer

# creating file uploader widget
uploaded_files = st.file_uploader("Upload your file here", type=["pdf","xls"], accept_multiple_files=True)

# Creating a function to parse PDF file
def pdf_extractor(uploaded_files):
    reader = PdfReader(uploaded_files)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

#creating a function to parse excel files
def excel_extractor(uploaded_files):
    xls= pd.ExcelFile(uploaded_files)
    sheets = {}
    for sheet_name in xls.sheet_names:
        sheets[sheet_name] = xls.parse(sheet_name)
    return sheets


# Document type identification by keywords
def detect_doc_type(text_or_df):
    keywords = {
        "income_statement" : ["revenue","income","profit","expense","tax"],
        "balance_sheet" : ["assets","liabilites","equity"],
        "cash_flow" : ["income","cash outflow","cash inflow"]
    }

    #Converting the uploaded file txt string into lower case for easy matching with keywords
    if isinstance(text_or_df,str):
        text = text_or_df.lower()
    else:
        text = "".join(map(str,text_or_df.columns)).lower()
    for doc_type,words in keywords.items():
        if any(word in text for word in words):
            return doc_type.replace("_","").title()
        return "Unknown Document Type"
    


# Displaying the uploaded file details
if uploaded_files is not None:
    for uploaded_file in uploaded_files:    
        st.subheader(f"{uploaded_file.name}")
        file_details = {"filename":uploaded_file.name,"filetype":uploaded_file.type,"filesize":uploaded_file.size}
        st.write(file_details)

        if uploaded_file.name.endswith(".pdf"):
            text = pdf_extractor(uploaded_file)
            doc_type =detect_doc_type(text)
            st.write(f"**Detected Document Type**{doc_type}")
            st.text_area("Extracted Text Preview",text[:1000])

        elif uploaded_file.name.endswith(".xls",".xlsx"):
            sheets = excel_extractor(uploaded_file)
            for sheet_name,df in sheets.items():
                st.write(f"Sheet:{sheet_name}")
                doc_type = detect_doc_type(df)
                st.write(f"**Detected Document Type:** {doc_type}")
                st.dataframe(df.head())



#if "documents" not in st.session_state:
#st.session_state["documents"] = {}#


# Collecting text from all the documents
all_text = ""

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pdf"):
            text = pdf_extractor(uploaded_file)
            all_text += text + "\n"
        elif uploaded_file.name.endswith(".xlsx",".xls"):
            sheets = excel_extractor(uploaded_file)
            for _,df in sheets.items():
                all_text +=df.to_string() + "\n"

# Intialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Create a chat interface
st.subheader("Ask Questions about your Financial Documents")

# display previous message
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#user question input
if question := st.chat_input("Ask financial question.."):
    st.chat_message("user").markdown(question)
    st.session_state.chat_history.append({"role":"user","content":question})

    #generate model response
    with st.spinner("Analyzing document.."):
        answer = generate_answer(all_text,question)
    
    st.chat_message("assistant").markdown(answer)
    st.session_state.chat_history.append({"role":"user", "content": answer})

    





