# Document Q&A Assistant — RAG Pipeline

Ask natural language questions about any PDF or Excel file. 
Get accurate, context-grounded answers — not hallucinations.

Built as a full end-to-end Retrieval Augmented Generation (RAG) system 
using local inference, meaning no data leaves your machine.

---

## Demo

> Upload a PDF → Ask "What are the key risks mentioned in section 3?" → 
> Get a precise, cited answer in seconds.

*(Screenshot coming soon — run locally to see it in action)*

---

## How it works
Document Upload → Parsing → Chunking → Embedding Generation
→ ChromaDB Vector Store → Semantic Search
→ Relevant Chunks + User Query → Llama3 (via Ollama) → Answer

**Why this architecture?**
- Chunking prevents token overflow and improves retrieval precision
- ChromaDB enables fast semantic search over embeddings
- Ollama + Llama3 keeps inference local — no API costs, no data exposure
- RAG grounds answers in your actual document, dramatically reducing hallucinations

---

## Tech stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Document parsing | PyMuPDF / openpyxl |
| Chunking & orchestration | LangChain |
| Embeddings | sentence-transformers |
| Vector store | ChromaDB |
| LLM inference | Llama3 via Ollama (local) |

---

## Setup

**Prerequisites:** Python 3.10+, [Ollama](https://ollama.com) installed and running locally.

```bash
# 1. Clone the repo
git clone https://github.com/MrunmayeeNaik/RAG-Documents-Assistance.git
cd RAG-Documents-Assistance

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull the Llama3 model via Ollama
ollama pull llama3

# 4. Run the app
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## Supported file types

- PDF documents
- Excel files (.xlsx)

---

## Design decisions & trade-offs

- **Chunk size:** Chose 500 tokens with 50-token overlap — balances context 
  preservation with retrieval precision. Larger chunks gave more context 
  but hurt search accuracy.
- **Local inference:** Ollama + Llama3 instead of OpenAI API — eliminates 
  API cost and keeps sensitive documents private. Trade-off is slower 
  inference on CPU-only machines.
- **ChromaDB over FAISS:** Simpler setup for persistent storage; 
  FAISS would be faster for very large corpora.

---

## Limitations & future improvements

- Currently handles single-document sessions (no multi-doc cross-referencing)
- Llama3 via Ollama is slow on machines without a GPU (~10–30s per query)
- Could add re-ranking (e.g. Cohere rerank) for better retrieval on long docs
- Planned: support for .docx and .txt formats

---

## What I learned

Designing the chunking strategy had the most impact on answer quality — 
more than model choice. Overlap between chunks was essential to avoid 
cutting off context at boundaries. I also learned that embedding model 
selection matters significantly; `all-MiniLM-L6-v2` outperformed larger 
models on short-query retrieval for this use case.
