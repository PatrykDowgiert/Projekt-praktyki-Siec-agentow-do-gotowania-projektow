import json
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Analizuję zależności między plikami...")
    
    requirements = state.get("requirements", "")
    plan = state.get("plan", [])[-1]
    existing_files = state.get("project_files", [])
    existing_names = [f['name'] for f in existing_files]
    
    llm = get_llm(model_role="coder") # Coder jest lepszy w strukturach JSON
    
    system_prompt = f"""Jesteś Głównym Architektem Oprogramowania.
    
    TWOJE ZADANIE:
    Zaprojektuj strukturę plików dla projektu i zdefiniuj zależności (kontekst).
    
    ISTNIEJĄCE PLIKI: {existing_names}
    
    ZASADY:
    1. Zwróć poprawny JSON w formacie listy obiektów:
       [
         {{ "filename": "utils.py", "context_needed": [] }},
         {{ "filename": "database.py", "context_needed": ["utils.py"] }},
         {{ "filename": "main.py", "context_needed": ["utils.py", "database.py"] }}
       ]
    2. "context_needed": Lista plików, które Programista musi przeczytać, żeby napisać dany plik (importy).
    3. KOLEJNOŚĆ MA ZNACZENIE! Najpierw pliki niezależne (np. config, utils), na końcu pliki główne.
    4. Jeśli plik już istnieje, ale wymaga zmian, też uwzględnij go na liście.
    5. NIE dodawaj żadnego tekstu poza JSON.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}\nPlan: {plan}")
    ]
    
    response = llm.invoke(messages)
    content = response.content.replace("```json", "").replace("```", "").strip()
    
    try:
        structure_json = json.loads(content)
        # structure_json to teraz lista słowników: [{'filename': '...', 'context_needed': [...]}, ...]
        
        print(f"👷 [Architekt]: Zaplanowano {len(structure_json)} plików z zależnościami.")
        for item in structure_json:
            print(f"   - {item['filename']} (Wymaga: {item['context_needed']})")
            
    except json.JSONDecodeError:
        print("❌ [Architekt]: Błąd generowania JSON. Próbuję fallback...")
        # Awaryjnie: prosta lista bez kontekstu
        lines = [l.strip() for l in content.split('\n') if "." in l]
        structure_json = [{"filename": f, "context_needed": []} for f in lines]

    return {
        "file_structure": structure_json, # Zapisujemy bogatszą strukturę
        "current_file_index": 0, 
        "messages": [response]
    }