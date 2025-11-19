from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def pm_node(state: AgentState):
    requirements = state.get("requirements", "")
    # Sprawdzamy, czy mamy już jakieś pliki w projekcie
    existing_files = state.get("project_files", [])
    
    mode = "MODYFIKACJA ISTNIEJĄCEGO PROJEKTU" if existing_files else "NOWY PROJEKT"
    print(f"\n🕵️  [PM]: Analiza ({mode})...")
    
    llm = get_llm(model_role="pm")
    
    # Tworzymy listę nazw plików, żeby PM wiedział co już mamy
    file_names = [f['name'] for f in existing_files]
    
    system_prompt = f"""Jesteś Product Managerem.
    
    KONTEKST SYTUACJI:
    Tryb pracy: {mode}
    Istniejące pliki: {file_names if file_names else "Brak"}
    
    TWOJE ZADANIE:
    Stwórz plan działania na podstawie wymagań użytkownika.
    
    ZASADY:
    1. Jeśli to "MODYFIKACJA": Twoim celem jest opisanie, co zmienić w istniejącej logice. Nie wymyślaj koła na nowo.
    2. Jeśli to "NOWY PROJEKT": Zaplanuj MVP od zera.
    3. Unikaj Scope Creep (nie dodawaj funkcji, o które nikt nie prosił).
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}")
    ]
    
    response = llm.invoke(messages)
    
    return {
        "plan": [response.content],
        "messages": [response]
    }