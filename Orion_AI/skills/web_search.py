import os
import requests
from dotenv import load_dotenv
from ddgs import DDGS

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

DEEP_RESEARCH_KEYWORDS = [
    "research paper", "study", "analysis", "literature",
    "arxiv", "journal", "peer reviewed", "explain in detail",
    "compare", "scientific", "thesis", "survey", "findings"
]

NEWS_KEYWORDS = [
    "news", "latest", "today", "current", "recent", "breaking",
    "update", "announce", "happened", "this week", "right now", "yesterday", "yesterdays", "today", "todays", "this month", "this year", "2024", "2025", "2026"
]


def _is_deep_research(query: str) -> bool:
    return any(kw in query.lower() for kw in DEEP_RESEARCH_KEYWORDS)


def _is_news_query(query: str) -> bool:
    return any(kw in query.lower() for kw in NEWS_KEYWORDS)


# --- DuckDuckGo (primary, free, no key) ---
def _search_duckduckgo(query: str, num_results: int = 5) -> list[dict]:
    try:
        is_news = _is_news_query(query)
        timelimit = "d" if is_news else None  # past 24hrs for news, no limit otherwise

        if is_news:
            print("[WebSearch] DuckDuckGo — filtering to last 24 hours")

        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results=num_results,
                timelimit=timelimit
            ))

        return [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
                "source": "DuckDuckGo"
            }
            for r in results
        ]
    except Exception as e:
        print(f"[WebSearch] DuckDuckGo error: {e}")
        return []


# --- Serper (fallback for everyday search) ---
def _search_serper(query: str, num_results: int = 5) -> list[dict]:
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        items = response.json().get("organic", [])
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": "Serper"
            }
            for item in items
        ]
    except Exception as e:
        print(f"[WebSearch] Serper error: {e}")
        return []


# --- Tavily (deep research) ---
def _search_tavily(query: str, num_results: int = 5) -> list[dict]:
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "max_results": num_results,
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        items = response.json().get("results", [])
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "source": "Tavily"
            }
            for item in items
        ]
    except Exception as e:
        print(f"[WebSearch] Tavily error: {e}")
        return []
def format_search_results(results: list[dict]) -> str:
    """Convert raw search results into LLM-ready formatted text."""
    if not results:
        return "No search results found."
    
    lines = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        snippet = r.get("snippet", "")
        url = r.get("url", "")
        lines.append(f"[{i}] {title}\n    {snippet}\n    Source: {url}")
    return "\n\n".join(lines)

def web_search_skill(query: str) -> dict:
    """
    Orion skill wrapper for web search.

    note: search() internally catches engine-level errors and returns [].
    This wrapper cannot distinguish "no results found" from "all engines failed."
    Both will return {success: True, data: []}. To fix, search() should raise
    on total failure (all engines exhausted) so the wrapper can catch it.
    """
    try:
        results = search(query)
        return {
            "skill": "web_search",
            "success": True,
            "data": format_search_results(results),  # now a string
            "error": None
        }
    except Exception as e:
        return {
            "skill": "web_search",
            "success": False,
            "data": None,
            "error": str(e)
        }

# --- Main Router ---
def search(query: str, num_results: int = 5) -> list[dict]:
    """
    Routing logic:
    - Deep research keywords → Tavily → fallback Serper
    - News/latest queries   → DuckDuckGo (last 24hrs) → fallback Serper
    - Everything else       → DuckDuckGo → fallback Serper
    """
    if _is_deep_research(query):
        print("[WebSearch] Using Tavily (deep research)")
        results = _search_tavily(query, num_results)
        if results:
            return results
        print("[WebSearch] Tavily failed, falling back to Serper")
        return _search_serper(query, num_results)

    print("[WebSearch] Using Serper")
    results = _search_serper(query, num_results)
    if results:
        return results

    print("[WebSearch] Serper failed, falling back to DuckDuckGo")
    return _search_duckduckgo(query, num_results)