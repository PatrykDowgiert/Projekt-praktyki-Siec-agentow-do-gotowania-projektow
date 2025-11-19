from typing import List, TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    Struktura danych, która jest przekazywana między agentami.
    To jest 'Pamięć Krótkotrwała' całego procesu.
    """
    # Oryginalne zapytanie użytkownika (lub treść PDF)
    requirements: str
    
    # Lista User Stories / Zadań stworzona przez PM-a
    plan: List[str]
    
    # Kod wygenerowany przez Programistę
    current_code: str
    
    # Wynik testów od QA (np. "FAILED: SyntaxError...")
    test_feedback: str
    
    # Licznik iteracji (żeby uniknąć pętli nieskończonej przy naprawianiu błędów)
    iteration_count: int
    
    # Historia wiadomości (wymagane przez LangGraph do chatu)
    # operator.add oznacza, że nowe wiadomości są dopisywane do listy, a nie nadpisywane
    messages: Annotated[List[BaseMessage], operator.add]