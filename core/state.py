from typing import List, TypedDict, Annotated, Dict, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    requirements: str           # Co użytkownik chce
    plan: List[str]             # Plan PM-a
    
    file_structure: List[str]   # Lista plików do zrobienia (np. ["main.py", "game.py"])
    current_file_index: int     # NOWOŚĆ: Który plik teraz robimy (0, 1, 2...)
    
    project_files: List[Dict[str, str]] # Gotowy kod: [{"name": "main.py", "content": "..."}]
    
    messages: Annotated[List[BaseMessage], operator.add] # Historia czatu