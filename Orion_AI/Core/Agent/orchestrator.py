import json
from Core.Agent.state import AgentState
from Core.Agent.schemas import Output, Observation
from interfaces.llm.groq_client import GroqClient
from Core.Agent.tools import TOOLS
from skills.response_synthesizer import build_prompt


class Orchestrator:
    CAP_REACHED = "__CAP_REACHED__"

    def __init__(self):
        self.llm = GroqClient()
        self.tools = TOOLS

    def next_output(self, state) -> Output:
        prompt = build_prompt(state, self.tools)
        response = self.llm.generate(prompt, temperature=0, json_mode=True)
        try:
            data = json.loads(response)
        except Exception:
            return Output(action="finish", reason="could not parse JSON", args={}, answer="(parse error)")
        return Output(
            action=data.get("action", "finish"),
            reason=data.get("reason", ""),
            args=data.get("args", {}),
            answer=data.get("answer"),
        )

    def run_loop(self, goal: str) -> str:
        state = AgentState(goal=goal)

        while state.iteration < state.max_iterations:
            output = self.next_output(state)

            if output.action == "finish":
                print(f"Finished after {state.iteration} step(s).")
                return output.answer or ""

            tool = self.tools.get(output.action)
            if tool is None:
                observation = Observation(success=False, tool=output.action,
                                          data=None, error=f"unknown tool: {output.action}")
            else:
                observation = tool.run(output.args)

            print(f"ran: {output.action} with {output.args}")
            state.add_step(output, observation)

        print(f"Stopped: hit the cap of {state.max_iterations} iterations.")
        return self.CAP_REACHED
