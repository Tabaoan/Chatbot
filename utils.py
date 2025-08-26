import re
from typing import List

_URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)

def clean_question_remove_uris(text: str) -> str:
    txt = _URL_RE.sub(" ", text or "")
    toks = [t for t in re.split(r"\s+", txt) if not t.lower().endswith(".pdf")]
    return re.sub(r"\s+", " ", " ".join(toks)).strip()

def chunk_text(s: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    s = (s or "").strip()
    if not s: return []
    chunks, start, n = [], 0, len(s)
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(s[start:end])
        if end == n: break
        start = max(0, end - overlap)
    return chunks

def build_context_from_hits(hits, max_chars: int = 6000) -> str:
    ctx, total = [], 0
    for idx, h in enumerate(hits, start=1):
        seg = f"[{idx}] {h.page_content.strip()}"
        if total + len(seg) > max_chars: break
        ctx.append(seg); total += len(seg)
    return "\n\n".join(ctx)
