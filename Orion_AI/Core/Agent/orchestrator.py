import json
from Core.Agent.state import AgentState
from Core.Agent.schemas import Output, Observation
from interfaces.llm.groq_client import GroqClient
from skills.web_search import search, web_search_skill
from skills.response_synthesizer import build_prompt_with_search, build_prompt_without_search, build_prompt_with_context
class Orchestrator:
    def __init__(self):
        self.llm = GroqClient()
        self.memory = []
        self.skills = {
            "web_search": web_search_skill,
            "build_prompt_with_search": build_prompt_with_search,
            "build_prompt_without_search": build_prompt_without_search,
            "build_prompt_with_context": build_prompt_with_context
        }
    def _decide_skills(self, query: str) -> dict:
        """
        Decides which skills to use based on the query.
        Returns:{skills: {"skills": skill_name, "reason": str}
        """
        decision_prompt = f"""
You are an AI system deciding whether a user query requires live web search.
Skill options
1. web_search:
   use for:
   - Use search if the query is about recent events, news, or dynamic info
   - Use search if the question likely requires up-to-date facts
   - Do NOT use search for general knowledge or explanations
Rules:
-List ALL the skills you will use to answer the query, and a brief reason for each.
-skill name should match the options provided above
-Return an empty array [] if query can be answered from general knowledge without search
-if unsure, default to using web_search

Respond ONLY in JSON format:
{{
"skills": skill names used (array),
"reason": "short explanation"
}}

Query: {query}
"""
        response = self.llm.generate(decision_prompt, temperature=0.0,json_mode=True)
        VALID_SKILLS = ["web_search"] 
        try:
            decision = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            return {"skills": ["web_search"], "reason": "classifier failed to parse JSON"}
        if "skills" not in decision or "reason" not in decision:
            return {"skills": ["web_search"], "reason": "classifier returned malformed keys"}
        
        if not isinstance(decision["skills"], list) or not isinstance(decision["reason"], str):
            return {"skills": ["web_search"], "reason": "skill field was not a list"}
        decision["skills"] = [skill for skill in decision["skills"] if skill in VALID_SKILLS]

        return decision
    def run(self, query: str) -> str:
        decision = self._decide_skills(query)
    
        results = []
    
        for skill_name in decision.get("skills", []):
            skill = self.skills.get(skill_name)
        
            if skill:
                try:
                    results.append(skill(query))
                except Exception as e:
                # Skill crashed — record as failed
                    results.append({
                        "skill": skill_name,
                        "success": False,
                        "data": None,
                        "error": str(e)
                    })
            else:
                results.append({
                    "skill": skill_name,
                    "success": False,
                    "data": None,
                    "error": "Skill not found in registry"
                })
    
        prompt = build_prompt_with_context(query, results)
    
        answer = self.llm.generate(prompt)
 
        self.memory.append({"role": "user", "content": query})
        self.memory.append({"role": "assistant", "content": answer})

        return answer

    CAP_REACHED = "__CAP_REACHED__"

    def run_loop(self, goal: str, get_next_output) -> str:
        
        state = AgentState(goal=goal)

        while state.iteration < state.max_iterations:
            output = get_next_output(state.iteration)

            if output.action == "finish":
                print(f"Finished after {state.iteration} step(s).")
                print(output.answer)
                print("\nHistory:\n" + state.render())
                return output.answer or ""

            print(f"would run: {output.action} with {output.args}")
            fake_obs = Observation(
                success=True,
                tool=output.action,
                data="(fake result)",
            )
            state.add_step(output, fake_obs)

        print(f"Stopped: hit the cap of {state.max_iterations} iterations.")
        print(state.render())
        return self.CAP_REACHED