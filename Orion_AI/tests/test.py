from Core.Agent.state import AgentState
from skills.response_synthesizer import build_prompt
from Core.Agent.tools import TOOLS  
from Core.Agent.orchestrator import Orchestrator
agent = Orchestrator()
print(agent.run_loop("Summarize what App/main.py does"))
print(agent.run_loop("What are the latest developments in AI this week?"))     # just the goal — no brain to pass