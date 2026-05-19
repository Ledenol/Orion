from Core.Agent.orchestrator import Orchestrator


class AssistantService:
    def __init__(self):
        self.orchestrator = Orchestrator()

    def ask(self, query: str) -> str:
        query = query.strip()
        
        if not query:
            return "I need a question to help you."
        
        return self.orchestrator.run(query)