# brainyai.py
# BrainyAI — minimal web+LLM Q&A (recruiter-friendly) with Groq + optional DuckDuckGo sources
#
# Run:
#   pip install streamlit requests duckduckgo-search
#   export GROQ_API_KEY="your_key_here"
#   streamlit run brainyai.py

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from duckduckgo_search import DDGS

# -----------------------------
# Config
# -----------------------------
APP_NAME = "BrainyAI"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_MODEL = "llama-3.3-70b-versatile"
MODEL_OPTIONS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
]


# -----------------------------
# Helpers
# -----------------------------
def clip(s: str, n: int) -> str:
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def ddg_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    query = (query or "").strip()
    if not query:
        return []

    results: List[Dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "title": (r.get("title") or "").strip(),
                        "url": (r.get("href") or "").strip(),
                        "snippet": (r.get("body") or "").strip(),
                    }
                )
    except Exception:
        # DDG can sometimes rate-limit. We fail gracefully.
        return []

    return [r for r in results if r.get("url")]


def groq_chat(
    user_query: str,
    model: str,
    web_results: Optional[List[Dict[str, str]]] = None,
    timeout_s: int = 45,
) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set.")

    web_results = web_results or []

    sources_block = ""
    if web_results:
        lines = []
        for i, r in enumerate(web_results, 1):
            title = clip(r.get("title", f"Source {i}"), 140)
            url = r.get("url", "")
            snippet = clip(r.get("snippet", ""), 260)
            lines.append(f"[S{i}] {title}\nURL: {url}\nSnippet: {snippet}")
        sources_block = "\n\n".join(lines)

    system = (
        "You are BrainyAI, a helpful assistant.\n"
        "Answer clearly, like ChatGPT.\n\n"
        "Rules:\n"
        "- If web sources are provided, use them.\n"
        "- If sources are missing/irrelevant, answer from general knowledge.\n"
        "- If the question is ambiguous, ask ONE short clarifying question.\n"
        "- If you use sources, end with: Sources: [S1], [S2] ...\n"
        "- Do not refuse unless impossible.\n"
    )

    user = f"User question:\n{user_query.strip()}\n"
    if sources_block:
        user += f"\nWeb sources:\n{sources_block}\n"

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    resp = requests.post(
        GROQ_BASE_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=timeout_s,
    )
    resp.raise_for_status()
    data = resp.json()
    return (data["choices"][0]["message"]["content"] or "").strip()


def run_query(query: str, use_web: bool, n_web: int, model: str):
    query = (query or "").strip()
    if not query:
        st.session_state.answer = "Type a question first."
        st.session_state.web = []
        return

    # Web results (optional)
    web_results = ddg_search(query, max_results=n_web) if use_web else []
    st.session_state.web = web_results

    # LLM answer (always attempt)
    try:
        st.session_state.answer = groq_chat(
            query,
            model=model,
            web_results=web_results if use_web else [],
        )
    except Exception as e:
        # Friendly non-scary errors (recruiter-friendly)
        msg = str(e)
        if "GROQ_API_KEY" in msg:
            st.session_state.answer = (
                "Setup needed: GROQ_API_KEY is missing.\n\n"
                "Add it to your environment and refresh."
            )
        else:
            st.session_state.answer = (
                "Temporary issue while generating the answer. Please try again.\n\n"
                f"Details: {clip(msg, 220)}"
            )


# -----------------------------
# Page + Session
# -----------------------------
st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="centered")

if "answer" not in st.session_state:
    st.session_state.answer = ""
if "web" not in st.session_state:
    st.session_state.web = []
if "query" not in st.session_state:
    st.session_state.query = ""
if "model" not in st.session_state:
    st.session_state.model = DEFAULT_MODEL

# -----------------------------
# Minimal, clean CSS
# - Moves search UI up
# - Makes toggle black/neutral (no red)
# -----------------------------
st.markdown(
    """
<style>
/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* Remove sidebar completely */
section[data-testid="stSidebar"] {display:none !important;}
div[data-testid="stSidebarNav"] {display:none !important;}

/* Page */
.stApp { background: #ffffff; color: #111; }
.block-container { max-width: 980px; padding-top: 14px; }

/* Hero positioning: bring content UP (not middle of page) */
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;   /* <— important */
  gap: 12px;
  padding-top: 70px;            /* <— adjusts vertical position (move up/down) */
}

/* Logo + bubble */
.logoDot {
  width: 44px; height: 44px; border-radius: 999px;
  background: #111;
  display:flex; align-items:center; justify-content:center;
  color:#fff; font-weight: 900;
}
.bubble {
  border: 1px solid rgba(0,0,0,0.10);
  border-radius: 999px;
  padding: 10px 14px;
  font-size: 14px;
  color: rgba(0,0,0,0.70);
  background: #fff;
}

/* Search card */
.searchCard {
  width: min(760px, 94%);
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 18px;
  padding: 16px;
  background: #fff;
  box-shadow: 0 14px 40px rgba(0,0,0,0.07);
}

/* Input */
.stTextInput input {
  border-radius: 14px !important;
  padding: 14px 14px !important;
  border: 1px solid rgba(0,0,0,0.12) !important;
  color: #111 !important;
  background: #fff !important;
  font-size: 15px !important;
}
.stTextInput input::placeholder { color: rgba(0,0,0,0.45) !important; }
.stTextInput input:focus {
  border-color: rgba(0,0,0,0.28) !important;
  box-shadow: 0 0 0 4px rgba(0,0,0,0.06) !important;
}

/* Buttons */
.stButton button {
  border-radius: 12px !important;
  font-weight: 700 !important;
  padding: 10px 16px !important;
  border: 1px solid rgba(0,0,0,0.12) !important;
  background: #fff !important;
  color: #111 !important;
}
.stButton button:hover {
  background: rgba(0,0,0,0.04) !important;
  border-color: rgba(0,0,0,0.22) !important;
}

/* Toggle: force neutral/black (Streamlit toggle is red by default sometimes) */
div[data-testid="stToggle"] label { gap: 10px; }
div[data-testid="stToggle"] span { color: rgba(0,0,0,0.75) !important; }
div[data-testid="stToggle"] div[role="switch"] {
  background: rgba(0,0,0,0.18) !important;
}
div[data-testid="stToggle"] div[role="switch"][aria-checked="true"] {
  background: #111 !important;
}
div[data-testid="stToggle"] div[role="switch"] > div {
  background: #fff !important;
}

/* Selects */
.stSelectbox div[data-baseweb="select"] { border-radius: 12px !important; }

/* Results */
.resultWrap {
  width: min(760px, 94%);
  margin: 18px auto 40px auto;
}
.card {
  border: 1px solid rgba(0,0,0,0.10);
  border-radius: 16px;
  padding: 14px;
  background:#fff;
}
.meta {
  font-size: 12px;
  color: rgba(0,0,0,0.55);
  margin-top: 10px;
}
.chips { display:flex; flex-wrap:wrap; gap:8px; margin-top: 10px; }
.chip {
  display:inline-flex;
  align-items:center;
  padding: 7px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,0.12);
  background: rgba(0,0,0,0.02);
  font-size: 12px;
  color: rgba(0,0,0,0.80) !important;
  text-decoration: none !important;
}
.chip:hover {
  border-color: rgba(0,0,0,0.25);
  background: rgba(0,0,0,0.04);
}
hr.soft {
  border: none;
  border-top: 1px solid rgba(0,0,0,0.08);
  margin: 14px 0;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# UI
# -----------------------------
st.markdown(
    """
<div class="hero">
  <div class="logoDot">🧠</div>
  <div class="bubble">Looking for something specific?</div>
  <div class="searchCard">
""",
    unsafe_allow_html=True,
)

# Form => Enter submits
with st.form("search_form", clear_on_submit=False):
    q = st.text_input(
        "",
        value=st.session_state.query,
        placeholder="Ask a question…",
        label_visibility="collapsed",
    )

    c1, c2, c3, c4 = st.columns([1.1, 0.9, 1.6, 0.8])
    with c1:
        use_web = st.toggle("Use web", value=True)
    with c2:
        n_web = st.selectbox("Sources", options=[3, 5, 6, 8], index=1, label_visibility="collapsed")
    with c3:
        model = st.selectbox("Model", options=MODEL_OPTIONS, index=MODEL_OPTIONS.index(st.session_state.model))
    with c4:
        submitted = st.form_submit_button("Search")

    st.caption("Tip: press Enter to search")

st.markdown("</div></div>", unsafe_allow_html=True)  # close searchCard + hero wrapper

if submitted:
    st.session_state.query = q
    st.session_state.model = model
    run_query(q, use_web=use_web, n_web=int(n_web), model=model)

# -----------------------------
# Results
# -----------------------------
if st.session_state.answer:
    st.markdown('<div class="resultWrap">', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Answer**")
    st.write(st.session_state.answer)
    st.markdown("</div>", unsafe_allow_html=True)

    if use_web and st.session_state.web:
        st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
        st.markdown("**Sources**")
        chips = ['<div class="chips">']
        for i, r in enumerate(st.session_state.web, 1):
            title = clip(r.get("title") or f"Source {i}", 48)
            url = r.get("url", "")
            if url:
                chips.append(f'<a class="chip" href="{url}" target="_blank">S{i} · {title}</a>')
        chips.append("</div>")
        st.markdown("\n".join(chips), unsafe_allow_html=True)

    st.markdown(
        f"<div class='meta'>Provider: Groq · Model: {st.session_state.model}"
        + (" · Web: DuckDuckGo" if use_web else " · Web: Off")
        + "</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 5])
    with cols[0]:
        if st.button("Clear"):
            st.session_state.answer = ""
            st.session_state.web = []
            st.session_state.query = ""
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Friendly hint if key is missing
if not GROQ_API_KEY:
    st.info("Set `GROQ_API_KEY` in your environment to enable answers.")