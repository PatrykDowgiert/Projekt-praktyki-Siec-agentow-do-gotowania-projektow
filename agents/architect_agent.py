import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def extract_json(text):
    """Wyciąga JSON z tekstu, nawet jak model doda komentarze."""
    try:
        # 1. Szukamy bloku w klamrach [ ... ]
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except:
        return None

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Analizuję zależności (Safe Mode)...")
    
    requirements = state.get("requirements", "")
    plan = state.get("plan", [])
    plan_str = plan[-1] if plan else ""
    existing_files = state.get("project_files", [])
    existing_names = [f['name'] for f in existing_files]
    
    llm = get_llm(model_role="coder")
    
    system_prompt = f"""Jesteś Architektem.
    ZADANIE: Zaprojektuj strukturę plików.
    
    Istniejące pliki: {existing_names}
    
    WYMAGANY FORMAT (Lista JSON):
    [
      {{ "filename": "main.py", "context_needed": [] }},
      {{ "filename": "utils.py", "context_needed": ["main.py"] }}
    ]
    
    ZASADA: Zwróć SAM JSON. Bez gadania.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}\nPlan: {plan_str}")
    ]
    
    response = llm.invoke(messages)
    content = response.content.strip()
    
    # --- BEZPIECZNE PARSOWANIE ---
    structure_json = extract_json(content)
    
    if not structure_json:
        print("⚠️ [Architekt]: Błąd JSON. Włączam tryb awaryjny (Fallback).")
        # Tryb awaryjny: szukamy linii wyglądających jak pliki
        lines = [l.strip() for l in content.split('\n') if "." in l and len(l.split()) == 1]
        # Tworzymy strukturę ręcznie
        structure_json = [{"filename": f, "context_needed": []} for f in lines]
        
    # Ostateczne zabezpieczenie przed None
    if not structure_json:
        structure_json = []

    print(f"👷 [Architekt]: Zaplanowano {len(structure_json)} plików.")

    return {
        "file_structure": structure_json,
        "current_file_index": 0, 
        "messages": [response]
    }