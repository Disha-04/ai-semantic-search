# BrainyAI (Semantic Web Q&A)

A minimal, recruiter-friendly AI assistant that answers **general questions** like ChatGPT and can optionally use **web sources (DuckDuckGo)** for fresher context — deployed with Streamlit.

**Live Demo:** https://ai-semantic-search-cpxebcxqckm6dqvtq4mnbc.streamlit.app/

---

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
