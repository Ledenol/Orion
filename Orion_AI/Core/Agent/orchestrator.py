import json
from Core.Agent.state import AgentState
from Core.Agent.schemas import Output, Observation
from interfaces.llm.openai_client import OpenAI_Client
from Core.Agent.tools import TOOLS
from skills.response_synthesizer import build_prompt
from Core.Agent.safety.approval import confirm

class Orchestrator:
    CAP_REACHED = "__CAP_REACHED__"

    def __init__(self):
        self.llm = OpenAI_Client()
        self.tools = TOOLS

    def next_output(self, state) -> Output:
        prompt = build_prompt(state, self.tools)
        response = self.llm.generate(prompt, temperature=0, json_mode=True)
        print("[RAW LLM RESPONSE]", repr(response))   # TEMP DEBUG
        try:
            data = json.loads(response)
        except Exception as e:
            print("[PARSE ERROR]", repr(e))            # TEMP DEBUG
            return Output(action="__parse_error__", reason="model returned invalid JSON", args={"error": str(e)}, answer=None)
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
                if tool.requires_approval:
                    if not confirm(output.action, output.args):
                        observation = Observation(success=False, tool=output.action,
                                                  data = None,error="user denied approval")
                    else:
                        observation = tool.run(output.args)
                elif tool.requires_approval is False:
                    observation = tool.run(output.args)
            print(f"ran: {output.action} with {output.args}")
            state.add_step(output, observation)

        print(f"Stopped: hit the cap of {state.max_iterations} iterations.")
        return self.CAP_REACHED
