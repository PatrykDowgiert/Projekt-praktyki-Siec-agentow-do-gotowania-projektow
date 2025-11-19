from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    
    if idx >= len(file_structure):
        return {}

    # Pobieramy zadanie (Qwen lepiej radzi sobie, jak dane są jasne)
    # file_structure to u nas lista słowników [{'filename': '...', 'context_needed': [...]}]
    # Ale musimy obsłużyć sytuację, gdyby Architekt zwrócił starą listę (samych stringów)
    task = file_structure[idx]
    
    if isinstance(task, dict):
        current_filename = task["filename"]
        context_needed = task.get("context_needed", [])
    else:
        current_filename = str(task)
        context_needed = [] # Fallback
    
    # --- SMART CONTEXT (Klucz do wydajności na Ollamie) ---
    smart_context = ""
    
    # 1. Dodajemy pliki wymagane (zależności)
    for needed_file in context_needed:
        found = next((f for f in existing_files_data if f["name"] == needed_file), None)
        if found:
            smart_context += f"\n# --- TREŚĆ PLIKU: {needed_file} ---\n{found['content']}\n"
    
    # 2. Sprawdzamy czy to edycja (czy plik już istnieje)
    old_file_content = None
    for f in existing_files_data:
        if f["name"] == current_filename:
            old_file_content = f["content"]
            break
            
    mode = "EDYCJA" if old_file_content else "TWORZENIE"
    
    print(f"\n👨‍💻 [Coder]: {mode} pliku: {current_filename}")
    
    llm = get_llm(model_role="coder")
    
    requirements = state.get("requirements", "")
    pm_plan = state.get("plan", [])[-1]

    # --- PROMPT POD QWEN-CODER ---
    # Qwen lubi konkrety. Nie bawimy się w diffy, bo Qwen jest szybki i lepiej mu idzie pisanie całości.
    
    if mode == "EDYCJA":
        system_prompt = f"""Jesteś Ekspertem Python (Qwen Coder).
        
        Twoim zadaniem jest zmodyfikować istniejący plik '{current_filename}'.
        
        STARY KOD PLIKU:
        ```python
        {old_file_content}
        ```
        
        ZALEŻNOŚCI (Inne pliki w projekcie):
        {smart_context}
        
        INSTRUKCJA:
        1. Przeanalizuj wymagania zmian.
        2. Napisz KOMPLETNY, POPRAWIONY kod pliku '{current_filename}'.
        3. Zwróć TYLKO kod (bez bloków markdown, jeśli to możliwe).
        """
        user_msg = f"Wymagania zmian: {requirements}\nPlan: {pm_plan}"
        
    else:
        # Tryb tworzenia
        system_prompt = f"""Jesteś Ekspertem Python (Qwen Coder).
        Piszesz nowy plik: '{current_filename}'.
        
        KONTEKST (Zależności):
        {smart_context if smart_context else "Brak (plik bazowy)."}
        
        INSTRUKCJA:
        1. Napisz profesjonalny kod dla pliku '{current_filename}'.
        2. Zadbaj o poprawne importy (patrz na kontekst).
        3. Zwróć TYLKO kod.
        """
        user_msg = f"Wymagania: {requirements}\nPlan: {pm_plan}"
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ]
    
    # Ollama czasem gada na początku, więc czyścimy wynik
    response = llm.invoke(messages)
    new_code = response.content
    
    # Czyścimy markdown (```python ... ```)
    new_code = new_code.replace("```python", "").replace("```", "").strip()
    
    # Jeśli model dodał na początku np. "Here is the code:", spróbujmy to wyciąć
    # (Prosta heurystyka: szukamy pierwszego importu lub def/class)
    if not new_code.startswith("import") and not new_code.startswith("from") and len(new_code) > 0:
         # Czasami Qwen pisze tekst przed kodem. Zostawiamy jak jest, bo trudno to idealnie wyciąć bez regexa,
         # ale zazwyczaj Qwen Coder jest bardzo grzeczny.
         pass

    # Aktualizacja pamięci
    updated_project_files = [f for f in existing_files_data if f["name"] != current_filename]
    updated_project_files.append({"name": current_filename, "content": new_code})
    
    return {
        "project_files": updated_project_files,
        "current_file_index": idx + 1,
        "messages": [response]
    }