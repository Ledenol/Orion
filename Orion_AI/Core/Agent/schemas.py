from dataclasses import dataclass , field 
from typing import Any, Optional
@dataclass
class Input:
    goal : str
    available_tools : list[str]
    rules : list[str]
    output_schema : list[str]
@dataclass
class Output:
    action : str #continue or finish
    reason : str
    args : dict[str, Any] = field(default_factory= dict)
    answer: Optional[str] = None
@dataclass
class Observation:
    success: bool
    tool: str
    data: Any
    error: Optional[str] = None
@dataclass
class HistoryStep:
    iteration: int
    output : Output
    observation: Optional[Observation] = None