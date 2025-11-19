from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Planuję strukturę plików (TRYB: Minimalistyczny)...")
    
    requirements = state.get("requirements", "")
    plan = state.get("plan", [])
    plan_str = plan[-1] if plan else ""
    
    llm = get_llm(model_role="coder")
    
    system_prompt = """Jesteś pragmatycznym Architektem Systemu.
    
    ZADANIE:
    Wypisz listę plików niezbędnych do uruchomienia projektu.
    
    ZASADY KRYTYCZNE:
    1. Generuj TYLKO pliki niezbędne do działania (Essential Only).
    2. Unikaj zbędnego boilerplate'u (żadnych dockerów, configów django, czy skryptów deployu, chyba że użytkownik wyraźnie o nie prosił).
    3. Format: Tylko nazwy plików, każda w nowej linii.
    4. Zawsze uwzględnij 'requirements.txt' jeśli są zewnętrzne biblioteki.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}\nPlan PM: {plan_str}")
    ]
    
    response = llm.invoke(messages)
    
    # Parsowanie i czyszczenie (usuwamy puste linie i komentarze)
    files = [line.strip() for line in response.content.split('\n') if line.strip() and not line.startswith("#")]
    
    # Zabezpieczenie: jeśli model się rozgada, bierzemy tylko linijki wyglądające jak pliki
    clean_files = []
    for f in files:
        # Akceptujemy tylko linie, które mają kropkę (rozszerzenie) i nie mają spacji w środku (zazwyczaj)
        if "." in f and len(f.split()) == 1:
            clean_files.append(f)
    
    print(f"👷 [Architekt]: Zaplanowano {len(clean_files)} plików: {clean_files}")
    
    return {
        "file_structure": clean_files,
        "current_file_index": 0,
        "project_files": [],
        "messages": [response]
    }