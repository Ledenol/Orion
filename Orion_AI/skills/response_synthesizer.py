def build_prompt_with_search(query: str, results: list[dict]) -> str:
    """
    Injects web search results into the LLM prompt so Groq can
    reason over fresh data instead of relying on its training cutoff.
    """
    if not results:
        return query  # No results — just send raw query
 
    # Format search results into readable context
    context_lines = []
    for i, r in enumerate(results, 1):
        context_lines.append(
            f"[{i}] {r['title']}\n"
            f"    Source: {r['url']}\n"
            f"    {r['snippet']}"
        )
 
    context = "\n\n".join(context_lines)
    source_used = results[0].get("source", "Web") if results else "Web"
 
    prompt = f"""You are Orion, a helpful research assistant with access to live web search results.
 
The following search results were retrieved from the web to help answer the user's question.
Use them as your primary source of information. Cite sources where relevant.
Do not rely on your training data for facts that may have changed — trust the search results.
 
Search source: {source_used}
 
--- SEARCH RESULTS ---
{context}
--- END OF RESULTS ---
 
User Question: {query}
 
Answer clearly and concisely based on the search results above:"""
 
    return prompt
 
 
def build_prompt_without_search(query: str) -> str:
    """
    Standard prompt when no web search is needed.
    """
    return f"""You are Orion, a helpful research assistant.
 
Answer the following question as accurately as possible.
If you are unsure or if this requires current information you may not have, say so clearly.
 
Question: {query}"""
def build_prompt_with_context(query: str, skill_results: list[dict]) -> str:
    """
    Builds an LLM prompt incorporating any successful skill outputs.
    Each skill's pre-formatted data is included as a section.
    If no skills ran or all failed, returns a basic prompt.
    """
    # Filter to successful skills only
    successful = [r for r in skill_results if r["success"]]
    
    if not successful:
        return f"""You are Orion, a helpful research assistant.

Answer the following question as accurately as possible.
If you are unsure or this requires current information you may not have, say so clearly, do not assume anything.

Question: {query}"""
    
    # Build sections from each successful skill's data
    sections = []
    for result in successful:
        skill_name = result["skill"]
        section = f"--- {skill_name.upper()} RESULTS ---\n{result['data']}\n--- END {skill_name.upper()} ---"
        sections.append(section)
    
    context = "\n\n".join(sections)
    
    return f"""You are Orion, an AI research assistant with access to tool outputs.

The following information was gathered by your tools to help answer the user's question.
Use this as your primary source. Cite sources where relevant.

{context}

User Question: {query}

Answer clearly and concisely based on the context above."""