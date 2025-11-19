import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def coder_node(state: AgentState):
    print("\n👨‍💻 [Coder]: Generuję zawartość plików...")
    
    file_structure = state.get("file_structure", [])
    requirements = state.get("requirements", "")
    
    llm = get_llm(model_role="coder")
    
    # Sklejamy listę plików w jeden string
    files_str = ", ".join(file_structure)
    
    system_prompt = """Jesteś Starszym Programistą Python.
    Twoim zadaniem jest wygenerowanie kodu dla CAŁEGO projektu na raz.
    
    ZASADA KRYTYCZNA:
    Twoja odpowiedź musi być POPRAWNYM kodem JSON w formacie:
    {
        "files": [
            { "name": "nazwa_pliku.py", "content": "kod..." },
            { "name": "requirements.txt", "content": "biblioteki..." }
        ]
    }
    
    1. Nie dodawaj żadnego tekstu przed ani po JSONie.
    2. Upewnij się, że JSON jest poprawny (zamknij klamry).
    3. W polach 'content' używaj znaków ucieczki dla nowych linii (\\n).
    """
    
    user_msg = f"""
    Projekt: {requirements}
    Wymagana lista plików do utworzenia: {files_str}
    
    Wygeneruj JSON z zawartością tych plików.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ]
    
    response = llm.invoke(messages)
    raw_content = response.content
    
    # --- PARSOWANIE JSON (Czyszczenie odpowiedzi LLM) ---
    # Czasami LLM doda ```json na początku. Usuwamy to.
    cleaned_json = raw_content.replace("```json", "").replace("```", "").strip()
    
    project_files = []
    try:
        data = json.loads(cleaned_json)
        project_files = data.get("files", [])
        print(f"👨‍💻 [Coder]: Wygenerowano {len(project_files)} plików.")
    except json.JSONDecodeError as e:
        print(f"❌ [Coder]: Błąd generowania JSONa: {e}")
        print("Treść:", raw_content[:100]) # Podgląd błędu
        # W wersji produkcyjnej tutaj powinna być pętla naprawcza "Self-Correction"
    
    return {
        "project_files": project_files,
        "messages": [response]
    }