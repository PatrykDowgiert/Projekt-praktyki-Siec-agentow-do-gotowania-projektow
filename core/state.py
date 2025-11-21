from typing import List, TypedDict, Annotated, Dict, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    requirements: str
    plan: List[str]
    file_structure: List[Dict[str, Any]] # lub List[str] w trybie awaryjnym
    project_files: List[Dict[str, str]]
    
    current_file_index: int
    
    # --- NOWE POLE: LICZNIK POPRAWEK ---
    retry_count: int
    # -----------------------------------
    
    test_feedback: str
    messages: Annotated[List[BaseMessage], operator.add]