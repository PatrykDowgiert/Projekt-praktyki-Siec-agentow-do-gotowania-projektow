import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def extract_code(text):
    if not text: return ""
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    match_gen = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match_gen: return match_gen.group(1).strip()
    return text

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    
    # Zabezpieczenie listy plików (usuwamy None)
    if existing_files_data is None: existing_files_data = []
    existing_files_data = [f for f in existing_files_data if f is not None]
    
    if not file_structure or idx >= len(file_structure):
        return {}

    task = file_structure[idx]
    if not task:
        return {"current_file_index": idx + 1}

    if isinstance(task, dict):
        current_filename = task.get("filename", "unknown.py")
        context_needed = task.get("context_needed", [])
    else:
        current_filename = str(task)
        context_needed = []
        
    # SMART CONTEXT - Tutaj był potencjalny błąd, teraz naprawiony
    smart_context = ""
    for needed_file in context_needed:
        # Szukamy pliku, ale sprawdzamy czy f nie jest None
        found = next((f for f in existing_files_data if f and f.get("name") == needed_file), None)
        if found:
            content = found.get("content", "")
            smart_context += f"\n# --- PLIK: {needed_file} ---\n{content}\n"
    
    old_file_content = None
    for f in existing_files_data:
        if f.get("name") == current_filename:
            old_file_content = f.get("content")
            break
            
    mode = "EDYCJA" if old_file_content else "TWORZENIE"
    print(f"\n👨‍💻 [Coder]: {mode} pliku: {current_filename}")
    
    llm = get_llm(model_role="coder")
    
    sys_prompt = f"Jesteś programistą Python. {'Edytujesz' if mode=='EDYCJA' else 'Tworzysz'} plik '{current_filename}'."
    user_msg = f"Wymagania: {state.get('requirements','')}\nKod w ```python ... ```."
    
    if mode == "EDYCJA": user_msg += f"\nSTARY KOD:\n{old_file_content}"
    user_msg += f"\nKONTEKST:\n{smart_context}"
    
    try:
        resp = llm.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=user_msg)])
        code = extract_code(resp.content)
    except Exception as e:
        print(f"Błąd LLM: {e}")
        code = "# Error generating code"

    # Aktualizacja
    updated = [f for f in existing_files_data if f.get("name") != current_filename]
    updated.append({"name": current_filename, "content": code})
    
    return {
        "project_files": updated,
        "current_file_index": idx + 1,
        "messages": [resp] if 'resp' in locals() else []
    }