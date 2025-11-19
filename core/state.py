from typing import List, TypedDict, Annotated, Dict, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    requirements: str           # Co użytkownik chce (Input)
    plan: List[str]            # Plan PM-a
    file_structure: List[str]  # Lista plików wymyślona przez Architekta
    project_files: List[Dict[str, str]] # Gotowy kod: [{"name": "main.py", "content": "print('hi')"}]
    test_feedback: str         # Feedback QA
    iteration_count: int       # Licznik pętli
    messages: Annotated[List[BaseMessage], operator.add]