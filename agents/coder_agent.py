import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def extract_code(text):
    """Wyciąga kod z ramek markdown."""
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    
    match_generic = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match_generic: return match_generic.group(1).strip()
    
    # Fallback: zwracamy całość, ale usuwamy linie "Here is code:"
    lines = text.split('\n')
    clean = [l for l in lines if not l.lower().startswith(("here", "sure", "below"))]
    return "\n".join(clean).strip()

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    
    if not file_structure or idx >= len(file_structure):
        return {} # Koniec pracy

    task = file_structure[idx]
    
    # --- ZABEZPIECZENIE PRZED BŁĘDEM 'NoneType' ---
    if task is None:
        print(f"⚠️ [Coder]: Puste zadanie pod indeksem {idx}. Pomijam.")
        return {"current_file_index": idx + 1} # Idziemy dalej mimo błędu

    if isinstance(task, dict):
        current_filename = task.get("filename", "unknown.py")
        context_needed = task.get("context_needed", [])
    else:
        current_filename = str(task)
        context_needed = []
    
    # --- Reszta logiki bez zmian (Smart Context) ---
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
    pm_plan = state.get("plan", [])
    pm_plan_str = pm_plan[-1] if pm_plan else ""

    if mode == "EDYCJA":
        system_prompt = f"""Jesteś Ekspertem Python. Zmodyfikuj plik '{current_filename}'.
        STARY KOD:
        ```python
        {old_file_content}
        ```
        ZALEŻNOŚCI:
        {smart_context}
        Zwróć TYLKO kod wewnątrz ```python ... ```.
        """
        user_msg = f"Wymagania: {requirements}\nPlan: {pm_plan_str}"
    else:
        system_prompt = f"""Jesteś Ekspertem Python. Napisz plik '{current_filename}'.
        ZALEŻNOŚCI:
        {smart_context}
        Zwróć TYLKO kod wewnątrz ```python ... ```.
        """
        user_msg = f"Wymagania: {requirements}\nPlan: {pm_plan_str}"
    
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_msg)]
    response = llm.invoke(messages)
    
    clean_code = extract_code(response.content)
    
    updated_project_files = [f for f in existing_files_data if f["name"] != current_filename]
    updated_project_files.append({"name": current_filename, "content": clean_code})
    
    return {
        "project_files": updated_project_files,
        "current_file_index": idx + 1,
        "messages": [response]
    }