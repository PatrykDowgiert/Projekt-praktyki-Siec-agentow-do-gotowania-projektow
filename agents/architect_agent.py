from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm
import json
import re

def extract_json(text):
    """Próbuje wyciągnąć JSON z tekstu."""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return None

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Planuję strukturę (Tryb Uniwersalny)...")
    
    requirements = state.get("requirements", "")
    existing_files = state.get("project_files", [])
    existing_names = [f['name'] for f in existing_files]
    
    llm = get_llm(model_role="coder") # Coder zna frameworki najlepiej
    
    # PROMPT UNIWERSALNY - ZMUSZA DO MYŚLENIA O KONKRETNYM FRAMEWORKU
    system_prompt = f"""Jesteś Głównym Architektem Oprogramowania (Senior Solutions Architect).
    
    ZADANIE:
    Stwórz strukturę plików dla projektu na podstawie wymagań.
    
    ZASADY KRYTYCZNE:
    1. ROZPOZNAJ TECHNOLOGIĘ:
       - Jeśli user chce **Django** -> zaplanuj `manage.py`, folder aplikacji, `settings.py`.
       - Jeśli user chce **.NET/C#** -> zaplanuj `Program.cs`, `Startup.cs`, plik `.csproj`.
       - Jeśli user chce **Angular/React** -> zaplanuj `package.json`, `index.html`, `src/App.js` itp.
       - Jeśli user chce **Python Script** -> zaplanuj `main.py`, `utils.py`.
    
    2. PODZIAŁ MODUŁOWY:
       - Nie wrzucaj wszystkiego do jednego pliku (chyba że to prosty skrypt).
       - Każdy plik musi mieć krótki opis `description` (co ma zawierać).
       
    3. FORMAT WYJŚCIOWY (JSON):
       [
         {{ "filename": "sciezka/do/pliku", "description": "Opis odpowiedzialności pliku" }},
         {{ "filename": "requirements.txt", "description": "Zależności" }}
       ]
    
    4. Zawsze dodaj `README.md`.
    
    Istniejące pliki: {existing_names}
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania projektu: {requirements}")
    ]
    
    structure = []
    
    try:
        response = llm.invoke(messages)
        structure = extract_json(response.content)
            
    except Exception as e:
        print(f"⚠️ [Architekt]: Błąd parsowania JSON: {e}")
    
    # --- GENERYCZNY FALLBACK (Zamiast Snake'a!) ---
    if not structure:
        print("⚠️ [Architekt]: Włączam tryb awaryjny (Generyczny).")
        # Jeśli nie udało się sparsować JSONa, próbujemy wyciągnąć chociaż nazwy plików z tekstu
        # lub dajemy absolutne minimum.
        structure = [
            {"filename": "main.py", "description": "Główny punkt wejścia programu."},
            {"filename": "utils.py", "description": "Funkcje pomocnicze."},
            {"filename": "README.md", "description": "Dokumentacja projektu."}
        ]

    # Budowanie finalnej struktury
    final_structure = []
    for item in structure:
        # Zabezpieczenie przed brakującymi kluczami
        fname = item.get("filename", "unknown.txt")
        desc = item.get("description", "Implementacja kodu")
        
        final_structure.append({
            "filename": fname,
            "description": desc,
            "context_needed": [] 
        })

    print(f"👷 [Architekt]: Zaplanowano: {[f['filename'] for f in final_structure]}")

    return {
        "file_structure": final_structure,
        "current_file_index": 0, 
        "messages": [response] if 'response' in locals() else []
    }