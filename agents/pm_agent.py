from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def pm_node(state: AgentState):
    """
    Rola: Product Manager
    Zadanie: Analiza wymagań i stworzenie listy zadań (User Stories).
    """
    print("\n🕵️  [PM]: Analizuję wymagania...")
    
    requirements = state.get("requirements", "")
    
    # Pobieramy model skonfigurowany jako 'pm' (np. llama3.3 lub qwen)
    llm = get_llm(model_role="pm")
    
    system_prompt = """Jesteś doświadczonym Product Managerem w zespole Agile.
    Twój cel: Przeanalizuj wymagania użytkownika i stwórz zwięzłą listę zadań (User Stories) niezbędnych do realizacji projektu.
    
    Zasady:
    1. Każde zadanie powinno być konkretne.
    2. Nie pisz kodu, tylko opisz funkcjonalność.
    3. Wynik zwróć jako punktowaną listę.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Oto wymagania projektu:\n{requirements}")
    ]
    
    response = llm.invoke(messages)
    plan_content = response.content
    
    print(f"🕵️  [PM]: Stworzyłem plan działania (Backlog).")
    
    # Aktualizujemy stan: zapisujemy plan i dodajemy wiadomość do historii
    return {
        "plan": [plan_content],
        "messages": [response]
    }