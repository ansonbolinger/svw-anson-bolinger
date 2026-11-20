"""RAG Search Tool for Alaska Department of Snow (ADS) Operations Manual."""

from pathlib import Path
from typing import List, Dict

KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ads_policy_manual.md"


def _load_chunks() -> List[Dict[str, str]]:
    if not KB_PATH.exists():
        return []
    text = KB_PATH.read_text(encoding="utf-8")
    raw_sections = text.split("\n## ")
    chunks = []
    for sec in raw_sections:
        if not sec.strip():
            continue
        lines = sec.strip().split("\n")
        title = lines[0].replace("#", "").strip()
        body = "\n".join(lines[1:]).strip()
        chunks.append({
            "title": title,
            "content": f"## {title}\n{body}"
        })
    return chunks


_CHUNKS = _load_chunks()


def search_ads_policy(query: str) -> str:
    """Searches the official Alaska Department of Snow (ADS) operational policies and emergency directives.

    Use this tool to find rules regarding:
    - Priority corridor classifications (Priority 1, 2, 3 response times)
    - Pass closure thresholds (wind, visibility, and avalanche risk limits for Thompson Pass, Turnagain Pass)
    - Equipment deployment standards (Alpha V-Plows, Bravo Rotary Blowers, Charlie chemical de-icers)
    - Public emergency broadcast levels (Green, Amber, Red).

    Args:
        query: Keywords or question regarding ADS winter road operations and directives.

    Returns:
        Relevant excerpt(s) from the ADS Operations Manual.
    """
    if not _CHUNKS:
        return "ADS Operations manual is currently unavailable."

    query_tokens = [w.lower() for w in query.split() if len(w) > 2]
    scored = []
    for chunk in _CHUNKS:
        text = chunk["content"].lower()
        title = chunk["title"].lower()
        score = 0
        for token in query_tokens:
            if token in title:
                score += 3
            if token in text:
                score += text.count(token)
        if score > 0:
            scored.append((score, chunk["content"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return f"No direct ADS policy matches found for '{query}'."
    return "\n\n---\n\n".join([content for _, content in scored[:2]])
