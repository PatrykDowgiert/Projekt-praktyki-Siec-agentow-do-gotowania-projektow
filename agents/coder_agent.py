from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def coder_node(state: AgentState):
    """
    Rola: Programista
    """
    print("\n👨‍💻 [Coder]: Piszę/Poprawiam kod...")
    
    tech_plan = state.get("plan", [])[-1]
    current_code = state.get("current_code", "")
    feedback = state.get("test_feedback", "")
    
    llm = get_llm(model_role="coder")
    
    # Sprawdzamy, czy to pierwsza wersja, czy poprawka
    if feedback and "FAILED" in feedback:
        print("   -> [Coder]: Otrzymałem błędy od QA. Naprawiam...")
        prompt_context = f"""
        To jest sesja naprawcza (Refactoring).
        
        Twój poprzedni kod:
        {current_code}
        
        Błędy zgłoszone przez QA:
        {feedback}
        
        Zadanie: Popraw powyższy kod, aby wyeliminować błędy. Zwróć CAŁY poprawiony kod.
        """
    else:
        prompt_context = f"""
        To jest nowa implementacja.
        Wytyczne Architekta:
        {tech_plan}
        """

    system_prompt = """Jesteś Starszym Programistą Python.
    Twoim zadaniem jest dostarczenie działającego, czystego kodu.
    
    Zasady:
    1. Pisz TYLKO kod (bez ```python na początku, jeśli to możliwe).
    2. Kod musi być kompletny.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt_context)
    ]
    
    response = llm.invoke(messages)
    code = response.content
    
    # Czasami modele dają tekst w markdown ```python ... ```. Usuńmy to dla czystości.
    code = code.replace("```python", "").replace("```", "").strip()
    
    print("👨‍💻 [Coder]: Gotowe.")
    
    return {
        "current_code": code,
        "messages": [response]
    }