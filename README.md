

## What BrainyAI Does

BrainyAI allows users to ask **natural language questions** and receive **context-aware answers** powered by semantic understanding rather than keyword matching.

It works by:
- Converting user queries into **vector embeddings**
- Searching semantically relevant documents using **FAISS**
- Using a **large language model (Groq)** to generate concise answers
- Optionally enhancing answers with **real-time web sources (DuckDuckGo)**

The result is a fast, intelligent Q&A system that explains *why* an answer was returned and, when enabled, shows **supporting sources**.

## 🚀 Live Demo
🔗 **Streamlit App:**  
https://ai-semantic-search-cpxebcxqckm6dqvtq4mnbc.streamlit.app/

### 🏠 Home Screen
![BrainyAI Home](brainyai home.png)

### 🔍 Search Query Example
!brainyai_search_query.png

### ⚙️ Settings Panel
![BrainyAI Settings](brainyai setting.png)
## What it does
- ✅ ChatGPT-style Q&A for *any* question
- ✅ Optional web lookup (DuckDuckGo) for supporting sources
- ✅ Clean Gemini/Google-like UI
- ✅ Fast responses using **Groq** LLM API

---

## Tech Stack
- **Frontend/UI:** Streamlit
- **LLM Provider:** Groq (OpenAI-compatible endpoint)
- **Web Sources:** DuckDuckGo Search (`duckduckgo-search`)
- **Language:** Python

---

## Features
- **Ask anything**: works for general queries (not limited to local notes)
- **Web-enhanced answers** (optional): adds source links when enabled
- **Minimal, premium UI**: simple search bar + answer + sources
- **Safe fallbacks**: shows a clean message if the API key is missing/invalid

---

## Quick Start (Local Run)

### 1) Clone
```bash
git clone https://github.com/Disha-04/ai-semantic-search.git
cd ai-semantic-search
