import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def apply_patches(original_code, response_content):
    """
    Funkcja magiczna: Szuka bloków SEARCH/REPLACE i aplikuje je na kod.
    """
    # Wzorzec szuka bloków:
    # <<<<SEARCH
    # ...
    # ====
    # ...
    # >>>>
    pattern = r"<<<<SEARCH\n(.*?)\n====\n(.*?)\n>>>>"
    patches = re.findall(pattern, response_content, re.DOTALL)
    
    if not patches:
        return None # Brak patchy, zakładamy że model zwrócił cały plik

    new_code = original_code
    for search_block, replace_block in patches:
        # Usuwamy ewentualne białe znaki z początku/końca bloku dla pewności
        if search_block in new_code:
            new_code = new_code.replace(search_block, replace_block)
            print("   -> 🔧 Zastosowano patch (zmiana fragmentu).")
        else:
            print("   -> ⚠️ OSTRZEŻENIE: Nie znaleziono fragmentu do podmienienia! (LLM pomylił spacje?)")
            # Fallback: W prawdziwym systemie tutaj użylibyśmy algorytmu 'fuzzy match',
            # ale teraz po prostu zwracamy stary kod + ostrzeżenie
            
    return new_code

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", []) 
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    
    if idx >= len(file_structure):
        return {}

    current_task = file_structure[idx]
    current_filename = current_task["filename"]
    context_needed = current_task.get("context_needed", [])
    
    # Budujemy Smart Context
    smart_context = ""
    for needed_file in context_needed:
        found = next((f for f in existing_files_data if f["name"] == needed_file), None)
        if found:
            smart_context += f"\n### PLIK: {needed_file} ###\n{found['content']}\n"
            
    # Sprawdzamy czy edytujemy
    old_file_content = None
    for f in existing_files_data:
        if f["name"] == current_filename:
            old_file_content = f["content"]
            break
            
    mode = "EDYCJA" if old_file_content else "TWORZENIE"
    
    print(f"\n👨‍💻 [Coder]: {mode} pliku {idx+1}/{len(file_structure)}: {current_filename}")

    llm = get_llm(model_role="coder")
    
    requirements = state.get("requirements", "")
    pm_plan = state.get("plan", [])[-1]

    if mode == "EDYCJA":
        # --- PROMPT DO OPTYMALIZACJI (PATCHING) ---
        system_prompt = f"""Jesteś Programistą Python. Edytujesz plik '{current_filename}'.
        
        AKTUALNA TREŚĆ:
        ```python
        {old_file_content}
        ```
        
        MASZ DWIE OPCJE EDYCJI:
        
        OPCJA 1 (Dla małych zmian - ZALECANA):
        Użyj formatu SEARCH/REPLACE, aby zmienić tylko fragment.
        <<<<SEARCH
        (dokładny fragment starego kodu, który chcesz usunąć)
        ====
        (nowy kod, który ma się tam znaleźć)
        >>>>
        
        OPCJA 2 (Dla dużych zmian):
        Zwróć po prostu CAŁY nowy kod pliku (bez znaczników SEARCH/REPLACE).
        
        ZASADA:
        Przy OPCJI 1 musisz skopiować blok SEARCH co do znaku (spacje, wcięcia), inaczej zmiana się nie uda!
        """
        user_msg = f"Zmień kod zgodnie z: {requirements}\nKontekst: {smart_context}"
        
    else:
        # Tworzenie od zera - tu zawsze zwracamy cały plik
        system_prompt = f"""Jesteś Programistą Python. Tworzysz nowy plik '{current_filename}'.
        Kontekst: {smart_context}
        Zwróć kompletny kod pliku.
        """
        user_msg = f"Wymagania: {requirements}\nPlan: {pm_plan}"
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ]
    
    response = llm.invoke(messages)
    raw_response = response.content
    
    final_code = ""
    
    if mode == "EDYCJA":
        # Próbujemy zaaplikować patche
        patched_code = apply_patches(old_file_content, raw_response)
        
        if patched_code:
            final_code = patched_code
        else:
            # Jeśli nie ma patchy, zakładamy, że model zwrócił cały plik (albo patchowanie się nie udało)
            # Czyścimy markdown
            final_code = raw_response.replace("```python", "").replace("```", "").strip()
            if len(final_code) < 10 and len(old_file_content) > 50:
                 # Zabezpieczenie: Jeśli model zwrócił coś b. krótkiego a nie był to patch,
                 # to pewnie błąd. Zostawiamy stary kod.
                 print("   -> ❌ Błąd: Model zwrócił za mało danych. Cofam zmiany.")
                 final_code = old_file_content
    else:
        final_code = raw_response.replace("```python", "").replace("```", "").strip()
    
    # Aktualizacja pamięci
    updated_project_files = [f for f in existing_files_data if f["name"] != current_filename]
    updated_project_files.append({"name": current_filename, "content": final_code})
    
    return {
        "project_files": updated_project_files,
        "current_file_index": idx + 1,
        "messages": [response]
    }