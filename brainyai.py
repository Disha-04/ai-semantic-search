# brainyai.py
# BrainyAI — Gemini-like premium single-screen UI (NO page scroll)
# Groq LLM + optional DuckDuckGo sources

from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests
import streamlit as st
from duckduckgo_search import DDGS


# -----------------------------
# Config
# -----------------------------
APP_NAME = "BrainyAI"
APP_ICON = "🧠"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_MODEL = "llama-3.3-70b-versatile"
MODEL_OPTIONS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]


# -----------------------------
# Helpers
# -----------------------------
def clip(s: str, n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def ddg_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    query = (query or "").strip()
    if not query:
        return []

    out: List[Dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                out.append(
                    {
                        "title": (r.get("title") or "").strip(),
                        "url": (r.get("href") or "").strip(),
                        "snippet": (r.get("body") or "").strip(),
                    }
                )
    except Exception:
        return []

    return [r for r in out if r.get("url")]


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
            lines.append(
                f"[S{i}] {clip(r.get('title',''),120)}\n"
                f"URL: {r.get('url','')}\n"
                f"Snippet: {clip(r.get('snippet',''),220)}"
            )
        sources_block = "\n\n".join(lines)

    system = (
        "You are BrainyAI, a helpful assistant.\n"
        "Answer clearly and concisely.\n"
        "If sources are provided, use them.\n"
        "If you use sources, end with: Sources: [S1], [S2] ...\n"
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
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
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

    web_results = ddg_search(query, max_results=n_web) if use_web else []
    st.session_state.web = web_results

    try:
        st.session_state.answer = groq_chat(
            query, model=model, web_results=web_results if use_web else []
        )
    except requests.HTTPError as e:
        code = getattr(e.response, "status_code", None)
        if code == 401:
            st.session_state.answer = (
                "Unauthorized (401). Your GROQ_API_KEY is missing/invalid.\n"
                "Fix: set GROQ_API_KEY correctly and restart."
            )
        else:
            st.session_state.answer = f"Request failed: {clip(str(e), 220)}"
    except Exception as e:
        st.session_state.answer = f"Error: {clip(str(e), 220)}"


# -----------------------------
# Streamlit setup
# -----------------------------
st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="centered")

for k, v in {
    "answer": "",
    "web": [],
    "query": "",
    "model": DEFAULT_MODEL,
    "use_web": True,
    "n_web": 5,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# -----------------------------
# Premium CSS: ONE-SCREEN + NO SCROLL
# -----------------------------
st.markdown(
    """
<style>
/* Hide Streamlit chrome */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header[data-testid="stHeader"] {background: transparent;}
section[data-testid="stSidebar"] {display:none !important;}
div[data-testid="stSidebarNav"] {display:none !important;}

/* IMPORTANT: NO PAGE SCROLL */
html, body { height: 100% !important; overflow: hidden !important; }
.stApp { height: 100vh !important; overflow: hidden !important; }

/* Centered container */
.block-container {
  height: 100vh !important;
  max-width: 980px;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Background (Gemini-like soft orbs) */
.stApp {
  background:
    radial-gradient(900px 420px at 30% 20%, rgba(120,170,255,.22), transparent 60%),
    radial-gradient(900px 420px at 70% 30%, rgba(255,170,220,.18), transparent 60%),
    radial-gradient(900px 420px at 55% 75%, rgba(255,230,160,.16), transparent 60%),
    #ffffff;
}

/* Shell */
.shell {
  width: min(760px, 92vw);
  text-align: center;
}

/* Brand */
.brand {
  font-size: 56px;
  line-height: 1.0;
  font-weight: 850;
  letter-spacing: -0.04em;
  margin: 0 0 22px 0;
  color: #0b0f17;
}

/* Search input */
.stTextInput input {
  height: 54px !important;
  border-radius: 999px !important;
  padding: 0 18px 0 46px !important;
  border: 1px solid rgba(11,15,23,0.14) !important;
  background: rgba(255,255,255,0.92) !important;
  font-size: 16px !important;
  box-shadow: 0 12px 34px rgba(0,0,0,0.08) !important;
}
.stTextInput input:focus {
  border-color: rgba(11,15,23,0.24) !important;
  box-shadow: 0 0 0 6px rgba(11,15,23,0.06), 0 14px 38px rgba(0,0,0,0.10) !important;
}

/* Search icon overlay */
.searchIcon {
  position: relative;
  width: min(760px, 92vw);
  height: 0;
  margin: -44px auto 0 auto;
}
.searchIcon span {
  position:absolute;
  left: 18px;
  top: -38px;
  font-size: 16px;
  opacity: 0.55;
}

/* Buttons */
.stButton button {
  height: 44px !important;
  border-radius: 999px !important;
  padding: 0 18px !important;
  font-weight: 700 !important;
  border: 1px solid rgba(11,15,23,0.14) !important;
  background: rgba(255,255,255,0.92) !important;
  color: rgba(11,15,23,0.90) !important;
}
.stButton button:hover {
  background: rgba(11,15,23,0.04) !important;
  border-color: rgba(11,15,23,0.22) !important;
}

/* Settings expander */
div[data-testid="stExpander"] {
  border: 1px solid rgba(11,15,23,0.10) !important;
  border-radius: 16px !important;
  background: rgba(255,255,255,0.70) !important;
  box-shadow: 0 12px 34px rgba(0,0,0,0.06);
  overflow: hidden;
}
div[data-testid="stExpander"] summary {
  font-weight: 700 !important;
}

/* Toggle neutral */
div[data-testid="stToggle"] div[role="switch"] { background: rgba(11,15,23,0.18) !important; }
div[data-testid="stToggle"] div[role="switch"][aria-checked="true"] { background: rgba(11,15,23,0.92) !important; }
div[data-testid="stToggle"] div[role="switch"] > div { background: #fff !important; }

/* Results: keep inside fixed height area (NO PAGE SCROLL) */
.resultsBox {
  margin-top: 16px;
  text-align: left;
  border: 1px solid rgba(11,15,23,0.10);
  border-radius: 18px;
  padding: 14px;
  background: rgba(255,255,255,0.92);
  box-shadow: 0 18px 50px rgba(0,0,0,0.08);
  max-height: 240px;   /* keeps hero one-screen */
  overflow: auto;      /* internal scroll only if answer is long */
}
.chips { display:flex; flex-wrap:wrap; gap:10px; margin-top: 10px; }
.chip {
  display:inline-flex;
  align-items:center;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(11,15,23,0.12);
  background: rgba(11,15,23,0.02);
  font-size: 12px;
  color: rgba(11,15,23,0.82) !important;
  text-decoration: none !important;
}
.chip:hover { border-color: rgba(11,15,23,0.22); background: rgba(11,15,23,0.04); }
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# UI (One-screen)
# -----------------------------
st.markdown('<div class="shell">', unsafe_allow_html=True)
st.markdown(f'<div class="brand">{APP_NAME}</div>', unsafe_allow_html=True)

with st.form("qform", clear_on_submit=False):
    q = st.text_input(
        label="",
        value=st.session_state.query,
        placeholder="Ask anything…",
        label_visibility="collapsed",
    )
    st.markdown('<div class="searchIcon"><span>🔎</span></div>', unsafe_allow_html=True)

    b1, b2 = st.columns([1, 1])
    with b1:
        go = st.form_submit_button("Search")
    with b2:
        clear = st.form_submit_button("Clear")

with st.expander("Settings", expanded=False):
    c1, c2, c3 = st.columns([1.2, 0.8, 1.8])
    with c1:
        use_web = st.toggle("Use web sources", value=st.session_state.use_web)
    with c2:
        n_web = st.selectbox("Sources", [3, 5, 6, 8], index=[3, 5, 6, 8].index(st.session_state.n_web))
    with c3:
        model = st.selectbox("Model", MODEL_OPTIONS, index=MODEL_OPTIONS.index(st.session_state.model))

if clear:
    st.session_state.answer = ""
    st.session_state.web = []
    st.session_state.query = ""
    st.rerun()

if go:
    st.session_state.query = q
    st.session_state.use_web = bool(use_web)
    st.session_state.n_web = int(n_web)
    st.session_state.model = model
    run_query(q, use_web=bool(use_web), n_web=int(n_web), model=model)

# Results (embedded; NO page scroll)
if st.session_state.answer:
    st.markdown('<div class="resultsBox">', unsafe_allow_html=True)
    st.markdown("**Answer**")
    st.write(st.session_state.answer)

    if st.session_state.use_web and st.session_state.web:
        st.markdown("**Sources**")
        chips = ['<div class="chips">']
        for i, r in enumerate(st.session_state.web, 1):
            title = clip(r.get("title") or f"Source {i}", 52)
            url = r.get("url", "")
            if url:
                chips.append(f'<a class="chip" href="{url}" target="_blank">S{i} · {title}</a>')
        chips.append("</div>")
        st.markdown("\n".join(chips), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

if not GROQ_API_KEY:
    st.warning("GROQ_API_KEY is not set. Add it to your terminal/secrets and restart.")

st.markdown("</div>", unsafe_allow_html=True)