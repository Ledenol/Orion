from Core.Agent.schemas import Output
from Core.Agent.orchestrator import Orchestrator    
def stub_provider(turn: int) -> Output:
    outputs = [
        Output(
            reason="I need to inspect the CLI entry point.",
            action="file_read",
            args={"path": "Orion_AI/App/main.py"},
        ),
        Output(
            reason="Now I need to inspect the service layer.",
            action="file_read",
            args={"path": "Orion_AI/services/assistant_service.py"},
        ),
        Output(
            reason="I have enough context to answer.",
            action="finish",
            answer="Done. I checked the first two files.",
        ),
    ]

    return outputs[turn]
def get_never_finish_output(turn: int) -> Output:
    return Output(
        reason=f"I am still gathering information on turn {turn + 1}.",
        action="file_read",
        args={"path": f"fake_file_{turn + 1}.py"},
    )
orchestrator=Orchestrator()
result = orchestrator.run_loop("know Orion", get_never_finish_output)
print(result)
'''
orchestrator.run_loop("know Orion",stub_provider)
'''