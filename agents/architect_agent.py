from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm
import json
import re

def extract_json(text):
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match: return json.loads(match.group(0))
    return None

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Planuję strukturę (Tryb Precyzyjny)...")
    
    requirements = state.get("requirements", "")
    existing_files = state.get("project_files", [])
    existing_names = [f['name'] for f in existing_files]
    
    llm = get_llm(model_role="coder")
    
    system_prompt = f"""Jesteś Głównym Architektem Oprogramowania.
    
    ZADANIE: Zaprojektuj strukturę plików dla projektu.
    
    ZASADY:
    1. Zwróć JSON: [{{ "filename": "...", "description": "..." }}]
    2. W 'description' bądź TECHNICZNYM EKSPERTEM. Nie pisz "logika gry", pisz:
       - "Klasa Snake: lista segmentów, ruch automatyczny co tick zegara, obsługa kolizji."
       - "Main: pętla while, zegar FPS, obsługa klawiszy zmieniających wektor ruchu."
    3. Zawsze dodaj 'requirements.txt' i 'README.md'.
    
    Istniejące pliki: {existing_names}
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}")
    ]
    
    structure = []
    try:
        response = llm.invoke(messages)
        structure = extract_json(response.content)
    except: pass
    
    if not structure:
        # Fallback z lepszymi opisami
        structure = [
            {"filename": "settings.py", "description": "Stałe: kolory, wymiary, FPS."},
            {"filename": "game.py", "description": "Logika biznesowa. Klasy i metody, bez pętli głównej."},
            {"filename": "main.py", "description": "Punkt wejścia. Importuje game.py. Zawiera pętlę aplikacji."},
            {"filename": "requirements.txt", "description": "Tylko zewnętrzne biblioteki (np. pygame). Bez standardowych."},
            {"filename": "README.md", "description": "Dokumentacja dla użytkownika końcowego."}
        ]

    final_structure = []
    for item in structure:
        final_structure.append({
            "filename": item.get("filename", "file"),
            "description": item.get("description", "Implementacja"),
            "context_needed": [] 
        })

    print(f"👷 [Architekt]: Zaplanowano: {[f['filename'] for f in final_structure]}")

    return {
        "file_structure": final_structure,
        "current_file_index": 0, 
        "messages": [response] if 'response' in locals() else []
    }