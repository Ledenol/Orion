from skills.web_search import web_search_skill
from Core.Agent.orchestrator import Orchestrator

# Create object
agent = Orchestrator()

# Test query
query = "What is the latest AI news?"

# Run
result = agent.run(query)

print(result)