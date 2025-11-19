import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def extract_code(text):
    """
    Wyciąga kod z bloków markdown ```python ... ```.
    Jeśli nie ma bloków, próbuje zwrócić całość, ale czyści znane śmieci.
    """
    # 1. Szukamy bloku kodu w ```python ... ```
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # 2. Jeśli nie ma 'python', szukamy samego ``` ... ```
    pattern_generic = r"```\s*(.*?)\s*```"
    match_generic = re.search(pattern_generic, text, re.DOTALL)
    if match_generic:
        return match_generic.group(1).strip()
    
    # 3. Fallback (Model nie dał ramek) - usuwamy typowe "gadanie"
    # Usuwamy linie, które nie wyglądają jak kod (prosta heurystyka)
    lines = text.split('\n')
    clean_lines = []
    started = False
    for line in lines:
        # Jeśli linia zaczyna się od import, def, class, from -> to na pewno kod
        if line.strip().startswith(("import ", "from ", "def ", "class ", "@", "#")):
            started = True
        
        # Jeśli jeszcze nie zaczęliśmy kodu, a linia to zwykły tekst -> pomijamy
        if not started and not line.strip().startswith(("#", "print", "if")):
            # Ryzykowne, ale wycina "Here is the code:"
            continue
            
        clean_lines.append(line)
        
    return "\n".join(clean_lines).strip()

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    
    if idx >= len(file_structure):
        return {}

    task = file_structure[idx]
    
    if isinstance(task, dict):
        current_filename = task["filename"]
        context_needed = task.get("context_needed", [])
    else:
        current_filename = str(task)
        context_needed = []
    
    # --- SMART CONTEXT ---
    smart_context = ""
    for needed_file in context_needed:
        found = next((f for f in existing_files_data if f["name"] == needed_file), None)
        if found:
            smart_context += f"\n# --- PLIK: {needed_file} ---\n{found['content']}\n"
    
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

    if mode == "EDYCJA":
        system_prompt = f"""Jesteś Ekspertem Python (Qwen Coder).
        
        ZADANIE: Zmodyfikuj plik '{current_filename}'.
        
        STARY KOD:
        ```python
        {old_file_content}
        ```
        
        ZALEŻNOŚCI:
        {smart_context}
        
        ZASADA ABSOLUTNA:
        Twój output zostanie zapisany bezpośrednio do pliku .py.
        NIE PISZ ŻADNEGO TEKSTU POZA KODEM.
        Kod musi być wewnątrz ```python ... ```.
        """
        user_msg = f"Wymagania zmian: {requirements}\nPlan: {pm_plan}"
        
    else:
        system_prompt = f"""Jesteś Ekspertem Python.
        Tworzysz plik: '{current_filename}'.
        
        ZALEŻNOŚCI:
        {smart_context if smart_context else "Brak."}
        
        ZASADA ABSOLUTNA:
        Zwróć kod wewnątrz ```python ... ```.
        Nie dodawaj wstępu ani zakończenia.
        """
        user_msg = f"Wymagania: {requirements}\nPlan: {pm_plan}"
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ]
    
    response = llm.invoke(messages)
    
    # UŻYWAMY NOWEJ FUNKCJI CZYSZCZĄCEJ
    clean_code = extract_code(response.content)
    
    updated_project_files = [f for f in existing_files_data if f["name"] != current_filename]
    updated_project_files.append({"name": current_filename, "content": clean_code})
    
    return {
        "project_files": updated_project_files,
        "current_file_index": idx + 1, # Przechodzimy do QA (jeśli dodasz) lub nast. pliku
        "messages": [response]
    }