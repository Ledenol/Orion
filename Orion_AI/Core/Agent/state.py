from Core.Agent.schemas import Input, Output, Observation, HistoryStep
from dataclasses import dataclass, field
@dataclass
class AgentState:
    goal: str
    history: list[HistoryStep] = field(default_factory=list)
    max_iterations: int = 8
    @property
    def iteration(self) -> int:
        return len(self.history)
    def add_step(self, output: Output, observation: Observation | None = None) -> HistoryStep:
        next_iteration = len(self.history) + 1

        history_step = HistoryStep(
            iteration=next_iteration,
            output=output,
            observation=observation,
        )

        self.history.append(history_step)
        return history_step
    def render(self) -> str:
        if not self.history:
            return "No previous steps This is the first step"
        blocks = []
        for step in self.history:
            output = step.output
            observation = step.observation

            if observation is None:
                observation_text = "no observation recorded yet"
            elif observation.success:
                observation_text = f"success = {observation.success}, tool = {observation.tool}, data = {observation.data}"
            else:
                observation_text = f"error = {observation.error}, tool = {observation.tool}, data = {observation.data}"

            block = (
                f"Step: {step.iteration}\n"
                f"Reason: {output.reason}\n"
                f"Action: {output.action}\n"
                f"Args: {output.args}\n"
                f"Observation: {observation_text}\n"
            )
            if output.answer is not None:
                block += f"\nAnswer: {output.answer}"

            blocks.append(block)
        
        return "\n\n".join(blocks)
