from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def coder_node(state: AgentState):
    """
    Rola: Programista (Developer)
    Zadanie: Pisanie kodu na podstawie wytycznych Architekta.
    """
    print("\n👨‍💻 [Coder]: Piszę kod...")
    
    # Pobieramy ostatni element planu (czyli wytyczne od Architekta)
    tech_plan = state["plan"][-1]
    
    # Pobieramy model zoptymalizowany do kodu (np. qwen3-coder)
    llm = get_llm(model_role="coder")
    
    system_prompt = """Jesteś Starszym Programistą Python (Senior Python Developer).
    Twoim zadaniem jest napisanie działającego kodu na podstawie wytycznych.
    
    Zasady:
    1. Pisz TYLKO kod oraz niezbędne komentarze.
    2. Nie używaj bloków markdown (```python), zwróć czystą treść, jeśli to możliwe, lub oznacz bloki wyraźnie.
    3. Kod musi być zgodny z nowoczesnymi standardami Pythona (PEP8).
    4. Uwzględnij obsługę błędów.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wytyczne Architekta:\n{tech_plan}")
    ]
    
    response = llm.invoke(messages)
    code = response.content
    
    print("👨‍💻 [Coder]: Kod gotowy.")
    
    return {
        "current_code": code,
        "messages": [response]
    }