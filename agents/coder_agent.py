import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def detect_language(filename):
    """
    Zwraca nazwę języka programowania na podstawie rozszerzenia pliku.
    Obsługuje szeroki wachlarz technologii (Web, Backend, Systemowe).
    """
    if "." not in filename:
        return "Programming"
        
    ext = filename.split(".")[-1].lower()
    
    mapping = {
        # Python & Data
        "py": "Python",
        "ipynb": "Jupyter Notebook",
        
        # Web (Frontend)
        "js": "JavaScript",
        "jsx": "React (JavaScript)",
        "ts": "TypeScript",
        "tsx": "React (TypeScript)",
        "html": "HTML5",
        "css": "CSS3",
        "scss": "SCSS",
        "vue": "Vue.js",
        
        # Backend & Systemowe
        "java": "Java",
        "cs": "C# (.NET)",   # <--- Kluczowe dla .NET
        "cpp": "C++",
        "c": "C",
        "h": "C++ Header",
        "go": "Go",
        "rs": "Rust",
        "php": "PHP",
        "rb": "Ruby",
        
        # Dane & Config
        "json": "JSON",
        "xml": "XML",        # <--- Kluczowe dla .csproj (.NET)
        "yaml": "YAML",
        "yml": "YAML",
        "toml": "TOML",
        "ini": "INI",
        "env": "Environment Variables",
        
        # Bazy danych
        "sql": "SQL",
        
        # Skrypty
        "sh": "Bash Script",
        "bat": "Batch Script",
        "ps1": "PowerShell",
        
        # Dokumentacja
        "md": "Markdown",
        "txt": "Text"
    }
    
    return mapping.get(ext, "Programming")

def extract_content(text, filename):
    """
    Inteligentne czyszczenie treści w zależności od pliku.
    """
    # 1. DLA REQUIREMENTS.TXT - MUSI BYĆ CZYSTE!
    if filename == "requirements.txt":
        # Usuwamy wszelkie ramki markdown
        text = text.replace("```text", "").replace("```", "").strip()
        # Usuwamy "pip install" jeśli model dodał
        lines = [l.strip() for l in text.split('\n') if l.strip() and not l.lower().startswith("here")]
        clean_lines = [l.replace("pip install ", "") for l in lines]
        return "\n".join(clean_lines)

    # 2. DLA README.MD - ZACHOWUJEMY STRUKTURĘ
    if filename.endswith(".md"):
        # Usuwamy tylko zewnętrzne ramki, jeśli obejmują całość
        match = re.match(r"^```markdown\s*(.*?)\s*```$", text, re.DOTALL)
        if match: return match.group(1).strip()
        match_gen = re.match(r"^```\s*(.*?)\s*```$", text, re.DOTALL)
        if match_gen: return match_gen.group(1).strip()
        return text.strip()

    # 3. DLA KODU (.py, .js)
    pattern = r"```[\w\+]*\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    
    # Fallback
    lines = text.split('\n')
    clean = [l for l in lines if not l.lower().strip().startswith(("here", "sure", "okay"))]
    return "\n".join(clean).strip()

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    
    if existing_files_data is None: existing_files_data = []
    
    if not file_structure or idx >= len(file_structure):
        return {}

    task = file_structure[idx]
    if not task: return {"current_file_index": idx + 1}

    # Pobieramy dane zadania
    if isinstance(task, dict):
        current_filename = task.get("filename", "unknown")
        # TO JEST NOWOŚĆ: Opis co ma być w pliku
        file_description = task.get("description", "Standardowa implementacja")
    else:
        current_filename = str(task)
        file_description = "Implementacja pliku"
        
    language = detect_language(current_filename)
    
    # Smart Context - Dajemy WSZYSTKIE dotychczasowe pliki jako kontekst
    # Żeby np. main.py widział co jest w settings.py
    smart_context = ""
    for f in existing_files_data:
        if f and f.get("name") != current_filename:
            smart_context += f"\n# --- PLIK ISTNIEJĄCY: {f['name']} ---\n{f.get('content', '')}\n"
    
    print(f"\n👨‍💻 [Coder]: Tworzę {current_filename} ({file_description})")
    
    llm = get_llm(model_role="coder")
    
    # --- RÓŻNE STRATEGIE PROMPTOWANIA ---

    if current_filename == "requirements.txt":
        system_prompt = "Jesteś ekspertem Python. Wypisz tylko nazwy bibliotek, każda w nowej linii. BEZ KOMENTARZY. BEZ ```."
        user_msg = f"Biblioteki potrzebne do projektu: {state.get('requirements', '')}"

    elif current_filename.endswith(".md"):
        system_prompt = "Jesteś Technical Writerem. Napisz profesjonalne README.md w stylu GitHub (Instalacja, Uruchomienie, Opis)."
        user_msg = f"Opisz ten projekt na podstawie kodu:\n{smart_context}"

    else:
        # PROMPT DLA KODU - ZAKAZ PISANIA CAŁEJ GRY
        system_prompt = f"""Jesteś Programistą {language}.
        
        TWOJE ZADANIE: Napisz kod TYLKO dla pliku: '{current_filename}'.
        
        OPIS TEGO PLIKU:
        "{file_description}"
        
        KONTEKST (Inne pliki w projekcie):
        {smart_context}
        
        ZASADY:
        1. NIE pisz całej aplikacji w jednym pliku! Implementuj TYLKO to, co należy do '{current_filename}'.
        2. Jeśli potrzebujesz zmiennych z innych plików (widocznych w kontekście), zaimportuj je (np. `from settings import SCREEN_WIDTH`).
        3. Zwróć kod w ```{language.lower()} ... ```.
        """
        user_msg = f"Wymagania ogólne: {state.get('requirements', '')}"

    try:
        resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_msg)])
        clean_content = extract_content(resp.content, current_filename)
    except Exception as e:
        print(f"Błąd LLM: {e}")
        clean_content = "# Error"

    updated = [f for f in existing_files_data if f.get("name") != current_filename]
    updated.append({"name": current_filename, "content": clean_content})
    
    return {
        "project_files": updated,
        "current_file_index": idx + 1,
        "messages": [resp] if 'resp' in locals() else []
    }