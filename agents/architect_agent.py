from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Planuję strukturę (Tryb Tekstowy)...")
    
    requirements = state.get("requirements", "")
    plan = state.get("plan", [])
    plan_str = plan[-1] if plan else ""
    existing_files = state.get("project_files", [])
    existing_names = [f['name'] for f in existing_files]
    
    llm = get_llm(model_role="coder")
    
    # PROMPT: Prosimy o prostą listę, a nie JSON
    system_prompt = f"""Jesteś Głównym Architektem.
    
    TWOJE ZADANIE:
    Wypisz listę plików niezbędnych do działania projektu.
    
    ISTNIEJĄCE PLIKI: {existing_names}
    
    ZASADY:
    1. Wypisz TYLKO nazwy plików.
    2. Każdy plik w nowej linii.
    3. NIE używaj punktorów, numeracji ani JSONa.
    4. NIE dodawaj opisów.
    
    Przykład:
    main.py
    utils.py
    requirements.txt
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}\nPlan: {plan_str}")
    ]
    
    try:
        response = llm.invoke(messages)
        content = response.content.strip()
    except Exception as e:
        print(f"⚠️ [Architekt]: Błąd LLM: {e}")
        content = "main.py"

    # --- PARSOWANIE (Zamiana tekstu na strukturę) ---
    file_list = []
    
    # Dzielimy po liniach
    lines = content.split('\n')
    
    for line in lines:
        clean_line = line.strip()
        # Usuwamy ewentualne punktory, jeśli model nie posłuchał (np. "- main.py")
        clean_line = clean_line.lstrip("-*1234567890. ").strip()
        
        # Ignorujemy puste linie i te bez kropki (rozszerzenia)
        if not clean_line or "." not in clean_line:
            continue
            
        # Ignorujemy linie typu "Here are the files:"
        if " " in clean_line and not clean_line.endswith(".py"): # Pliki rzadko mają spacje
            continue
            
        file_list.append(clean_line)
        
    # Zabezpieczenie: Jeśli lista pusta, dodajemy domyślne pliki
    if not file_list:
        print("⚠️ [Architekt]: Model nie zwrócił plików. Daję domyślne.")
        file_list = ["main.py", "README.md"]

    # --- KONWERSJA NA STRUKTURĘ DLA CODERA ---
    # Zamieniamy ['main.py'] na [{'filename': 'main.py', 'context_needed': []}]
    # W tym trybie uproszczonym kontekst będzie budowany dynamicznie przez wszystkich
    structure_json = []
    for f in file_list:
        structure_json.append({
            "filename": f,
            "context_needed": [] # Coder sam dobierze, lub damy mu wszystko co mamy
        })

    print(f"👷 [Architekt]: Zaplanowano {len(structure_json)} plików: {file_list}")

    return {
        "file_structure": structure_json,
        "current_file_index": 0, 
        "messages": [response] if 'response' in locals() else []
    }