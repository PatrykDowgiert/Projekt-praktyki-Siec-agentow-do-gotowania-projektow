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

def extract_content(text, filename):
    # DLA REQUIREMENTS - Czyścimy brutalnie
    if filename == "requirements.txt":
        text = text.replace("`", "").replace("python", "").replace("bash", "")
        lines = [l.strip() for l in text.split('\n') if l.strip() and not l.lower().startswith(("here", "sure", "pip"))]
        return "\n".join(lines)

    # DLA README - Bierzemy wszystko
    if filename.endswith(".md"):
        # Usuwamy zewnętrzne ramki markdown jeśli są
        match = re.match(r"^```markdown\s*(.*?)\s*```$", text, re.DOTALL)
        if match: return match.group(1).strip()
        match_gen = re.match(r"^```\s*(.*?)\s*```$", text, re.DOTALL)
        if match_gen: return match_gen.group(1).strip()
        
        # Usuwamy gadanie "Here is the readme"
        lines = text.split('\n')
        if lines and lines[0].lower().startswith(("here", "sure", "certainly")):
            return "\n".join(lines[1:]).strip()
        return text.strip()

    # DLA KODU
    pattern = r"```[\w\+]*\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    return text

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files_data = state.get("project_files", [])
    if existing_files_data is None: existing_files_data = []

    if not file_structure or idx >= len(file_structure): return {}
    task = file_structure[idx]
    if not task: return {"current_file_index": idx + 1}

    current_filename = task.get("filename", "unknown") if isinstance(task, dict) else str(task)
    file_description = task.get("description", "Implementacja") if isinstance(task, dict) else "Kod"
    
    language = detect_language(current_filename)
    
    # Budujemy kontekst (WSZYSTKIE PLIKI)
    smart_context = ""
    for f in existing_files_data:
        if f and f.get("name") != current_filename:
            smart_context += f"\n# --- PLIK ISTNIEJĄCY: {f['name']} ---\n{f.get('content', '')}\n"
            
    print(f"\n👨‍💻 [Coder]: Tworzę {current_filename} ({file_description})")
    llm = get_llm(model_role="coder")
    
    # --- SPECJALNE PROMPTY ---

    if current_filename == "requirements.txt":
        system_prompt = """Jesteś ekspertem Python. 
        ZADANIE: Przeanalizuj kod w KONTEKŚCIE. Wypisz biblioteki zewnętrzne (pip), które są importowane.
        
        ZASADY:
        1. NIE wypisuj bibliotek standardowych (os, sys, time, random, math, json, re).
        2. Wypisz np. 'pygame', 'requests', 'flask', 'pandas'.
        3. Jeśli nie ma zewnętrznych bibliotek, zwróć pusty tekst.
        4. Format: czysta lista, nazwa biblioteki w nowej linii. BEZ KOMENTARZY.
        """
        user_msg = f"Kod projektu:\n{smart_context}"

    elif current_filename.lower().endswith(".md"):
        system_prompt = """Jesteś profesjonalnym Technical Writerem.
        
        ZADANIE: Wygeneruj plik README.md dla projektu na podstawie dostarczonego kodu.
        
        ZASADY KRYTYCZNE:
        1. NIE ZADAWAJ PYTAŃ. NIE PROŚ O KOD. MASZ GO PONIŻEJ.
        2. Przeanalizuj sekcję 'KOD PROJEKTU' i na jej podstawie opisz co ten program robi.
        3. Jeśli kod to gra Snake -> opisz sterowanie i zasady.
        4. Struktura: Tytuł, Opis, Technologie, Instalacja, Uruchomienie.
        5. Od razu generuj treść pliku.
        """
        user_msg = f"KOD PROJEKTU (Źródło prawdy):\n{smart_context}"

    else:
        # Kod programu
        system_prompt = f"""Jesteś Ekspertem {language}.
        ZADANIE: Napisz kod pliku '{current_filename}'.
        
        SZCZEGÓŁY IMPLEMENTACJI:
        "{file_description}"
        
        KONTEKST PROJEKTU:
        {smart_context}
        
        ZASADY:
        1. Implementuj dokładnie to, co jest w opisie.
        2. Jeśli to gra Snake: wąż rusza się SAM (co tick), klawisze tylko zmieniają kierunek.
        3. Zwróć kod w bloku markdown ```{language.lower()} ... ```.
        """
        user_msg = f"Wymagania usera: {state.get('requirements', '')}"

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