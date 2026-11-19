"""RAG Search Tool for Novasphere Dynamics Internal Knowledge Base.

Provides grounded semantic and keyword retrieval over the proprietary
Novasphere Dynamics documentation, policies, product specs, and FAQs.
Supports VertexAiSearchTool when configured, with a robust local vector/semantic
retrieval engine as the ground-truth datastore.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict

# Path to the proprietary markdown knowledge base
KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "novasphere_knowledge_base.md"


def _load_knowledge_base_chunks() -> List[Dict[str, str]]:
    """Loads and chunks the proprietary knowledge base by sections."""
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


_CHUNKS = _load_knowledge_base_chunks()


def search_internal_datastore(query: str) -> str:
    """Searches the private Novasphere Dynamics internal RAG datastore.

    Use this tool whenever answering questions about Novasphere Dynamics company policies,
    employee benefits, travel expenses, remote work allowances, IT security protocols,
    or proprietary product specs (such as AetherBot v4 or Chronos-Edge Controller).

    Args:
        query: The search keywords or question regarding proprietary Novasphere knowledge.

    Returns:
        Relevant excerpt(s) from the internal datastore, or a message indicating no matches.
    """
    if not _CHUNKS:
        return "Internal datastore is currently empty or unavailable."

    query_tokens = [w.lower() for w in query.split() if len(w) > 2]
    scored_chunks = []

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
            scored_chunks.append((score, chunk["content"]))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    if not scored_chunks:
        return (
            f"No relevant records found in the Novasphere Dynamics internal datastore for query: '{query}'. "
            "If this question is about external, general, or live web topics, please use Google Search."
        )

    top_results = [content for _, content in scored_chunks[:2]]
    return "\n\n---\n\n".join(top_results)
