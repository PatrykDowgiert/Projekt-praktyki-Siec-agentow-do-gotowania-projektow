import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def detect_language(filename):
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    mapping = {
        "py": "Python", "js": "JavaScript", "ts": "TypeScript", "html": "HTML5",
        "css": "CSS3", "java": "Java", "cpp": "C++", "c": "C", "cs": "C#",
        "go": "Go", "rs": "Rust", "php": "PHP", "sql": "SQL", "sh": "Bash Script",
        "json": "JSON", "xml": "XML", "yaml": "YAML", "md": "Markdown"
    }
    return mapping.get(ext, "Programming")

def extract_content(text, file_extension):
    # Szukamy dowolnego bloku kodu
    pattern = r"```[\w\+]*\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    
    # Fallback: czyszczenie tekstu
    lines = text.split('\n')
    clean = [l for l in lines if not l.lower().strip().startswith(("here", "sure", "okay", "below", "code"))]
    return "\n".join(clean).strip()

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    
    if existing_files_data is None: existing_files_data = []
    existing_files_data = [f for f in existing_files_data if f is not None]
    
    if not file_structure or idx >= len(file_structure):
        return {}

    task = file_structure[idx]
    if not task: return {"current_file_index": idx + 1}

    if isinstance(task, dict):
        current_filename = task.get("filename", "unknown")
        context_needed = task.get("context_needed", [])
    else:
        current_filename = str(task)
        context_needed = []
        
    # Wykrywanie
    language = detect_language(current_filename)
    is_docs = current_filename.lower().endswith((".md", ".txt"))
    
    # Smart Context
    smart_context = ""
    for needed_file in context_needed:
        found = next((f for f in existing_files_data if f and f.get("name") == needed_file), None)
        if found:
            smart_context += f"\n# --- PLIK: {needed_file} ---\n{found.get('content', '')}\n"
    
    old_file_content = None
    for f in existing_files_data:
        if f.get("name") == current_filename:
            old_file_content = f.get("content")
            break
            
    mode = "EDYCJA" if old_file_content else "TWORZENIE"
    print(f"\n👨‍💻 [Coder]: {mode} pliku: {current_filename} (Język: {language})")
    
    llm = get_llm(model_role="coder")
    requirements = state.get("requirements", "")
    
    if is_docs:
        # --- PROMPT DLA DOKUMENTACJI (NAPRAWIONY) ---
        # Ten prompt wymusza analizę kodu i zakazuje halucynacji
        system_prompt = """Jesteś Technical Writerem. Twoim zadaniem jest napisać README.md dla tego konkretnego projektu.
        
        ZASADY KRYTYCZNE (PRZESTRZEGAJ ICH!):
        1. ANALIZA: Przeczytaj uważnie kod z sekcji 'Kontekst projektu'. Opisz TO co tam widzisz.
        2. ZAKAZ HALUCYNACJI: Nie pisz o React, Flask, API czy bazie danych, jeśli nie ma ich w kodzie! Jeśli to gra w węża, pisz o wężu.
        3. STRUKTURA: 
           - Tytuł i realny opis
           - Instrukcja instalacji (np. pip install pygame)
           - Instrukcja uruchomienia (np. python main.py)
        4. JĘZYK: Polski.
        """
        user_msg = f"Napisz treść pliku: {current_filename}\n\nKontekst projektu (KOD ŹRÓDŁOWY):\n{smart_context}"
        
    else:
        # --- PROMPT DLA KODU ---
        system_prompt = f"""Jesteś Ekspertem w języku {language}.
        {'Edytujesz' if mode=='EDYCJA' else 'Tworzysz'} plik '{current_filename}'.
        
        ZASADY:
        1. Pisz kod zgodnie z najlepszymi praktykami dla języka {language}.
        2. Zwróć TYLKO kod wewnątrz bloku markdown (np. ```{language.lower()} ... ```).
        3. Uważaj na typy zmiennych (np. nie dodawaj krotki do obiektu, jeśli klasa tego nie obsługuje).
        """
        
        user_msg = f"Wymagania: {requirements}\n\nZALEŻNOŚCI (Inne pliki):\n{smart_context}"
        if mode == "EDYCJA": 
            user_msg += f"\nSTARY KOD:\n{old_file_content}"

    try:
        resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_msg)])
        extension = "." + current_filename.split(".")[-1] if "." in current_filename else ".txt"
        clean_content = extract_content(resp.content, extension)
    except Exception as e:
        print(f"Błąd LLM: {e}")
        clean_content = "# Error generating content"

    updated = [f for f in existing_files_data if f.get("name") != current_filename]
    updated.append({"name": current_filename, "content": clean_content})
    
    return {
        "project_files": updated,
        "current_file_index": idx + 1,
        "messages": [resp] if 'resp' in locals() else []
    }