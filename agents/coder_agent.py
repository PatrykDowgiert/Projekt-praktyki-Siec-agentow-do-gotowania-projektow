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
    """
    Wyciąga treść w zależności od typu pliku.
    Naprawia problem ucinania README.
    """
    # Usuwamy typowe "gadanie" modelu na początku (np. "Here is the code:")
    lines = text.split('\n')
    # Usuwamy pierwsze linie, jeśli to tylko gadanie
    if lines and lines[0].lower().strip().startswith(("here", "sure", "okay", "certainly", "below")):
        text = "\n".join(lines[1:]).strip()

    # --- LOGIKA DLA DOKUMENTACJI (.md, .txt) ---
    if file_extension in [".md", ".txt"]:
        # Jeśli model zamknął CAŁOŚĆ w ```markdown ... ```, zdejmujemy to.
        # Ale uważamy, żeby nie zdjąć wewnętrznych bloków kodu!
        
        # Sprawdzamy, czy cały tekst jest w jednej wielkiej ramce
        match_wrapper = re.match(r"^```markdown\s*(.*?)\s*```$", text, re.DOTALL)
        if match_wrapper:
            return match_wrapper.group(1).strip()
            
        match_gen = re.match(r"^```\s*(.*?)\s*```$", text, re.DOTALL)
        if match_gen:
            return match_gen.group(1).strip()
            
        # Jeśli nie ma głównej ramki, zwracamy CAŁY tekst (bo w Markdown tekst jest wymieszany z kodem)
        return text.strip()

    # --- LOGIKA DLA KODU (.py, .js, itp.) ---
    else:
        # Tutaj chcemy być restrykcyjni - bierzemy tylko to co w ramkach
        pattern = r"```[\w\+]*\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match: return match.group(1).strip()
        
        # Fallback
        return text.strip()

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
        
    language = detect_language(current_filename)
    is_docs = current_filename.lower().endswith((".md", ".txt"))
    
    # Smart Context
    smart_context = ""
    for needed_file in context_needed:
        found = next((f for f in existing_files_data if f and f.get("name") == needed_file), None)
        if found:
            # Dla README dajemy kod, żeby wiedział o czym pisać
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
        # PROMPT DLA DOKUMENTACJI
        system_prompt = """Jesteś Technical Writerem. Twoim zadaniem jest napisać README.md.
        
        ZASADY:
        1. Przeanalizuj kod w 'Kontekście' i opisz ten konkretny projekt.
        2. Struktura: Tytuł, Opis Funkcjonalności, Technologie, Instalacja, Uruchomienie.
        3. Używaj Markdown (nagłówki #, listy -, pogrubienia **).
        4. NIE wklejaj całych plików źródłowych.
        5. Pisz w języku polskim.
        """
        user_msg = f"Napisz treść pliku: {current_filename}\n\nKOD PROJEKTU:\n{smart_context}"
        
    else:
        # PROMPT DLA KODU
        system_prompt = f"""Jesteś Ekspertem w języku {language}.
        {'Edytujesz' if mode=='EDYCJA' else 'Tworzysz'} plik '{current_filename}'.
        
        ZASADY:
        1. Pisz kod zgodnie z najlepszymi praktykami.
        2. Zwróć TYLKO kod wewnątrz bloku markdown (np. ```{language.lower()} ... ```).
        """
        
        user_msg = f"Wymagania: {requirements}\n\nZALEŻNOŚCI:\n{smart_context}"
        if mode == "EDYCJA": 
            user_msg += f"\nSTARY KOD:\n{old_file_content}"

    try:
        resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_msg)])
        extension = "." + current_filename.split(".")[-1] if "." in current_filename else ".txt"
        
        # Wywołujemy nową, naprawioną funkcję ekstrakcji
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