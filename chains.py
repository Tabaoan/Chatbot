from typing import Any, Dict, List, Literal
import requests
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from config import llm, TAVILY_API_KEY
from prompt import CLASSIFY_SYS, SOLVE_SYS, GENERAL_SYS
from utils import build_context_from_hits, clean_question_remove_uris
from retrieval import retriever, ingest_fixed_pdf

parser = JsonOutputParser()

# ===== Classifier =====
def _classify_prompt(i: Dict[str, Any]):
    q = i["q"]; history = i.get("history", [])
    context_info = ""
    if history:
        recent = history[-6:]
        context_info = "\n\nNgữ cảnh gần đây:\n" + "\n".join(
            f"- {getattr(m, 'content', '')[:100]}..." for m in recent
        )
    return [
        {"role": "system", "content": CLASSIFY_SYS + context_info},
        {"role": "user", "content": f"Q: {q}\nTrả JSON với khóa label, confidence:"},
    ]

classify_chain = (
    RunnableLambda(lambda i: {"q": i["message"].strip(), "history": i.get("history", [])})
    | RunnableParallel(
        parsed=(RunnableLambda(_classify_prompt) | llm | parser),
        q=RunnableLambda(lambda x: x["q"]),
        history=RunnableLambda(lambda x: x["history"]),
    )
    | RunnableLambda(lambda d: {**d["parsed"], "q": d["q"], "history": d["history"]})
)

# ===== Tavily =====
def tavily_search(query: str, max_results: int = 5, search_depth: str = "advanced") -> Dict[str, Any]:
    r = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}", "Content-Type": "application/json"},
        json={"query": query, "max_results": max_results, "include_answer": True, "search_depth": search_depth},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()

def run_tavily(i: Dict[str, Any]) -> Dict[str, Any]:
    q = i["q"]; history = i.get("history", [])
    enhanced = q
    if history:
        short = [m.content for m in history[-4:] if hasattr(m, "content") and len(m.content) < 200]
        if short: enhanced = f"{' '.join(short)} {q}"
    try:
        data = tavily_search(enhanced)
        hits = data.get("results", [])
        cites = "; ".join(h.get("url","") for h in hits[:2] if h.get("url"))
        advice = "\n".join(f"- {h.get('content') or h.get('title')}" for h in hits[:2])
        return {"answer": advice or "Không tìm thấy hướng dẫn phù hợp.", "source": f"Tavily: {cites}"}
    except Exception as e:
        return {"answer": f"Lỗi khi tìm kiếm: {e}", "source": "Tavily Error"}

tavily_chain = RunnableLambda(run_tavily)

# ===== VectorDB =====
def run_vectordb(i: Dict[str, Any]) -> Dict[str, Any]:
    q_raw = i["q"]; hist: List[BaseMessage] = i.get("history", [])
    try:
        ingest_fixed_pdf()
    except Exception as e:
        print(f"Warning ingest: {e}")

    q = clean_question_remove_uris(q_raw)
    hits = retriever.invoke(q)
    if not hits:
        return {"answer": "Không tìm thấy đoạn nào phù hợp trong PDF...", "source": "VectorDB"}

    context = build_context_from_hits(hits, max_chars=6000)
    messages = [SystemMessage(content=SOLVE_SYS)]
    if hist: messages.extend(hist)
    messages.append(HumanMessage(content=f"Câu hỏi/bài tập: {q}\n\nCác trích đoạn:\n{context}\n\nHãy giải chi tiết."))

    try:
        solution = llm.invoke(messages).content
    except Exception as e:
        raw = "\n\n".join(f"- {h.page_content}" for h in hits)
        return {"answer": f"Không gọi được LLM... {e}\n\n{raw}", "source": ", ".join(h.metadata.get("source","") for h in hits)}
    cites = ", ".join(h.metadata.get("source","") for h in hits)
    return {"answer": solution, "source": f"VectorDB: {cites}"}

vectordb_chain = RunnableLambda(run_vectordb)

# ===== General =====
def run_general(i: Dict[str, Any]) -> Dict[str, Any]:
    q = i["q"]; hist: List[BaseMessage] = i.get("history", [])
    messages = [SystemMessage(content=GENERAL_SYS)]
    if hist: messages.extend(hist)
    messages.append(HumanMessage(content=q))
    try:
        response = llm.invoke(messages).content
        return {"answer": response, "source": "General Knowledge"}
    except Exception as e:
        return {"answer": f"Lỗi xử lý: {e}", "source": "Error"}

general_chain = RunnableLambda(run_general)

# ===== Memory wrapper (dùng cho app.py) =====
store: Dict[str, ChatMessageHistory] = {}
def get_history(sid: str):
    if sid not in store:
        store[sid] = ChatMessageHistory()
    return store[sid]

def make_chatbot(runnable):
    return RunnableWithMessageHistory(
        runnable,
        get_history,
        input_messages_key="message",
        history_messages_key="history",
    )
