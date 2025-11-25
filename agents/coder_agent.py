import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def detect_language(filename):
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    mapping = {
        "py": "Python", "js": "JavaScript", "ts": "TypeScript", "html": "HTML5",
        "css": "CSS3", "cs": "C#", "java": "Java", "cpp": "C++", "json": "JSON",
        "md": "Markdown", "txt": "Text"
    }
    return mapping.get(ext, "Programming")

def clean_requirements(text):
    """
    Brutalne czyszczenie requirements.txt. 
    Usuwa wszystko, co nie wygląda jak nazwa biblioteki.
    """
    # Usuwamy markdown i zbędne znaki
    text = text.replace("```", "").replace("txt", "").replace("python", "")
    
    valid_lines = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Ignorujemy komentarze i gadanie modelu
        if line.startswith("#") or " " in line: continue
        
        # Ignorujemy kod Pythona
        if any(x in line for x in ["import", "from", "def", "class", "=", "print", "sudo", "pip"]):
            continue
            
        # Ignorujemy biblioteki standardowe
        if line in ["os", "sys", "time", "random", "math", "re", "json", "unittest"]:
            continue
            
        # Jeśli linia to np. "pygame" lub "pandas>=1.0" -> akceptujemy
        valid_lines.append(line)
        
    return "\n".join(valid_lines)

def clean_readme(text):
    """
    Usuwa bloki kodu z README, zostawiając opis.
    """
    # Usuwamy zewnętrzne ramki markdown
    match = re.match(r"^```markdown\s*(.*?)\s*```$", text, re.DOTALL)
    if match: text = match.group(1)
    match_gen = re.match(r"^```\s*(.*?)\s*```$", text, re.DOTALL)
    if match_gen: text = match_gen.group(1)
    
    lines = text.split('\n')
    final_lines = []
    
    # Prosta heurystyka: usuwamy linie, które wyglądają jak czysty kod Pythona, 
    # chyba że są w bloku kodu (dla uproszczenia usuwamy nadmiarowe bloki)
    for line in lines:
        l = line.strip()
        # Jeśli linia zaczyna się od importowania kodu, a nie jest w bloku ``` - to śmieć
        if l.startswith(("import ", "from ", "def ", "class ", "if __name__")):
            continue
        final_lines.append(line)
        
    return "\n".join(final_lines).strip()

def extract_content(text, filename):
    # 1. SPECIAL CASE: REQUIREMENTS
    if filename == "requirements.txt":
        return clean_requirements(text)

    # 2. SPECIAL CASE: README
    if filename.endswith(".md"):
        return clean_readme(text)

    # 3. CODE FILES
    pattern = r"```[\w\+]*\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    
    # Fallback dla kodu - jeśli brak ramek, próbujemy odfiltrować gadanie
    lines = text.split('\n')
    code_lines = [l for l in lines if not l.lower().strip().startswith(("here", "sure", "okay", "below"))]
    return "\n".join(code_lines).strip()

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    if existing_files_data is None: existing_files_data = []

    if not file_structure or idx >= len(file_structure): return {}
    
    # Pobieranie zadania
    task = file_structure[idx]
    if not task: return {"current_file_index": idx + 1}

    current_filename = task.get("filename", "unknown") if isinstance(task, dict) else str(task)
    file_description = task.get("description", "Kod źródłowy") if isinstance(task, dict) else "Kod"
    
    language = detect_language(current_filename)
    
    # --- SMART CONTEXT (Tylko nazwy plików i nagłówki, żeby nie mieszać modelu) ---
    # Zamiast całych plików, dajemy mu pełny kontekst tylko jeśli to konieczne
    smart_context = ""
    for f in existing_files_data:
        if f and f.get("name") != current_filename:
            # Dajemy tylko pierwsze 500 znaków z innych plików, żeby Coder wiedział co tam jest,
            # ale nie kopiował ich całości.
            content_preview = f.get('content', '')[:1000] 
            smart_context += f"\n# --- PLIK ISTNIEJĄCY: {f['name']} ---\n{content_preview}\n... (reszta ukryta) ...\n"

    print(f"\n👨‍💻 [Coder]: Tworzę {current_filename}")
    
    llm = get_llm(model_role="coder")
    
    # --- PROMPTY SPECJALNE ---

    if current_filename == "requirements.txt":
        system_prompt = """Jesteś ekspertem Python.
        ZADANIE: Na podstawie analizy importów w projekcie, wypisz listę bibliotek do 'requirements.txt'.
        
        ZASADY:
        1. Wypisz TYLKO nazwy bibliotek (np. pygame, requests).
        2. Każda w nowej linii.
        3. ŻADNEGO KODU. Żadnych 'import', żadnych 'pip install'.
        4. Jeśli nie ma zewnętrznych bibliotek, nic nie pisz.
        """
        user_msg = f"Wymagania usera: {state.get('requirements', '')}"

    elif current_filename.lower().endswith(".md"):
        system_prompt = """Jesteś Technical Writerem.
        ZADANIE: Napisz krótki, czytelny plik README.md.
        
        ZASADY:
        1. Opisz co robi projekt.
        2. Podaj komendę instalacji i uruchomienia.
        3. NIE WKLEJAJ KODU ŹRÓDŁOWEGO (Usera to nie obchodzi).
        4. Użyj nagłówków Markdown.
        """
        user_msg = f"Nazwa projektu: {state.get('project_name', 'Projekt')}\nOpis: {state.get('requirements', '')}"

    else:
        # --- PROMPT DLA KODU (MODUŁOWY) ---
        system_prompt = f"""Jesteś Programistą {language}.
        Twoim zadaniem jest napisać kod TYLKO dla pliku: '{current_filename}'.
        
        OPIS ZADANIA DLA TEGO PLIKU:
        "{file_description}"
        
        ZASADY KRYTYCZNE:
        1. NIE PISZ CAŁEJ APLIKACJI. Pisz tylko ten jeden moduł/plik.
        2. Jeśli to 'settings.py' -> pisz tylko zmienne.
        3. Jeśli to 'snake.py' -> pisz tylko klasę. Nie dodawaj 'if __name__ == main' ani pętli gry, jeśli to nie jest main.py.
        4. Traktuj inne pliki w kontekście jako "read-only" - importuj z nich, ale nie przepisuj ich kodu tutaj.
        5. Zwróć kod w ```{language.lower()} ... ```.
        """
        user_msg = f"Wymagania: {state.get('requirements', '')}\n\nKONTEKST PROJEKTU:\n{smart_context}"

    try:
        resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_msg)])
        # Wywołujemy nową funkcję czyszczącą
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