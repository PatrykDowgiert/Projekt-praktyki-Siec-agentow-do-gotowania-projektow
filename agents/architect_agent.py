from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Planuję strukturę plików...")
    
    # Jeśli to kontynuacja rozmowy, nie musimy generować struktury od nowa,
    # chyba że użytkownik o to prosi. (Dla uproszczenia tutaj generujemy zawsze).
    
    requirements = state.get("requirements", "")
    plan = state.get("plan", [])
    plan_str = plan[-1] if plan else ""
    
    llm = get_llm(model_role="coder")
    
    system_prompt = """Jesteś Architektem Systemu.
    Na podstawie wymagań wypisz listę plików niezbędnych do działania projektu.
    
    Zasady:
    1. Wypisz TYLKO nazwy plików (np. main.py, utils.py).
    2. Każda nazwa w nowej linii.
    3. Nie dodawaj opisów ani numeracji.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}\nPlan: {plan_str}")
    ]
    
    response = llm.invoke(messages)
    
    # Parsowanie: dzielimy po liniach i usuwamy puste
    files = [line.strip() for line in response.content.split('\n') if line.strip() and not line.startswith("#")]
    
    print(f"👷 [Architekt]: Zaplanowano {len(files)} plików: {files}")
    
    return {
        "file_structure": files,
        "current_file_index": 0, # Resetujemy licznik plików na start
        "project_files": [],     # Resetujemy pliki (nowy start)
        "messages": [response]
    }