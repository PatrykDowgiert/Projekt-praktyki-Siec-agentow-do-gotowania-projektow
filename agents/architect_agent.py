import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Analizuję zależności (BULLETPROOF MODE)...")
    
    requirements = state.get("requirements", "")
    plan = state.get("plan", [])
    plan_str = plan[-1] if plan else ""
    existing_files = state.get("project_files", [])
    existing_names = [f['name'] for f in existing_files]
    
    llm = get_llm(model_role="coder")
    
    system_prompt = f"""Jesteś Architektem.
    ZADANIE: Zaprojektuj strukturę plików.
    Istniejące pliki: {existing_names}
    
    Zwróć CZYSTY JSON w formacie:
    [
      {{ "filename": "main.py", "context_needed": [] }}
    ]
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}\nPlan: {plan_str}")
    ]
    
    try:
        response = llm.invoke(messages)
        content = response.content
    except Exception as e:
        print(f"⚠️ [Architekt]: Błąd LLM: {e}")
        content = ""

    # --- LOGIKA AWARYJNA (FALLBACK) ---
    structure_json = []
    
    # 1. Próba Regex
    match = re.search(r"\[.*\]", content, re.DOTALL)
    if match:
        try:
            structure_json = json.loads(match.group(0))
        except:
            pass

    # 2. Jeśli pusto -> Spadochron (Hardcoded Fallback)
    if not structure_json or not isinstance(structure_json, list):
        print("⚠️ [Architekt]: Nie udało się sparsować JSON. Włączam tryb awaryjny.")
        # Tworzymy chociaż jeden plik, żeby proces poszedł dalej
        structure_json = [{"filename": "main.py", "context_needed": []}]

    # 3. FILTROWANIE NULLI (To naprawia Twój błąd!)
    # Usuwamy z listy wszystko, co nie jest słownikiem
    safe_structure = []
    for item in structure_json:
        if isinstance(item, dict) and "filename" in item:
            safe_structure.append(item)
        elif isinstance(item, str):
            # Naprawiamy, jeśli model zwrócił listę stringów zamiast obiektów
            safe_structure.append({"filename": item, "context_needed": []})
            
    print(f"👷 [Architekt]: Zaplanowano {len(safe_structure)} plików.")

    return {
        "file_structure": safe_structure,
        "current_file_index": 0, 
        "messages": [response] if 'response' in locals() else []
    }