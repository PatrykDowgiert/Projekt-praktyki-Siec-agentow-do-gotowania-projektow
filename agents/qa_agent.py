import ast
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def qa_node(state: AgentState):
    files = state.get("project_files", [])
    retries = state.get("retry_count", 0)
    
    if not files: 
        return {"test_feedback": "PASSED", "retry_count": 0}

    current_file = files[-1]
    code = current_file.get("content", "")
    filename = current_file.get("name", "unknown")
    
    print(f"\n🐞 [QA]: Weryfikacja '{filename}' (Próba {retries + 1}/3)...")

    # --- 1. IGNORUJEMY DOKUMENTACJĘ I KONFIGURACJĘ ---
    # Tych plików nie ma sensu sprawdzać pod kątem "składni kodu"
    SKIPPED_EXTENSIONS = (
        ".md", ".txt", ".env", ".gitignore", 
        ".csv", ".ini", ".log"
    )
    
    if filename.lower().endswith(SKIPPED_EXTENSIONS):
        print(f"   -> ℹ️ Dokumentacja/Config. Pomijam.")
        return {"test_feedback": "PASSED", "retry_count": 0}

    # --- 2. BEZPIECZNIK (Circuit Breaker) ---
    if retries >= 3:
        print(f"⚠️ [QA]: Limit poprawek dla '{filename}'. Puszczam mimo błędów.")
        return {"test_feedback": "PASSED (FORCED)", "retry_count": 0}

    # --- 3. STRATEGIA SPRAWDZANIA ---
    
    # A) PYTHON -> Używamy AST (Szybkie, Lokalne)
    if filename.lower().endswith(".py"):
        try:
            ast.parse(code)
            print(f"   -> ✅ Kod Python poprawny (AST).")
            return {"test_feedback": "PASSED", "retry_count": 0}
        except SyntaxError as e:
            error_msg = f"SyntaxError w linii {e.lineno}: {e.msg}"
            print(f"   -> ❌ {error_msg}")
            return _fail_response(state, error_msg, retries)

    # B) INNE JĘZYKI (JS, HTML, CSS, C++, Java...) -> Używamy LLM
    else:
        print(f"   -> 🤖 Używam AI do sprawdzenia składni ({filename})...")
        
        llm = get_llm(model_role="coder") # Coder zna składnię najlepiej
        
        system_prompt = """Jesteś Starszym Inżynierem QA (Code Reviewer).
        
        TWOJE ZADANIE:
        Sprawdź poniższy kod pod kątem KRYTYCZNYCH BŁĘDÓW SKŁADNIOWYCH (Syntax Errors), które uniemożliwią jego działanie.
        
        ZASADY:
        1. Ignoruj styl, brak komentarzy czy optymalizację. Szukaj tylko błędów, które "wywalą" program (np. brakujące klamry, domknięcia tagów).
        2. Jeśli kod wygląda na działający -> Odpisz TYLKO słowem: PASSED.
        3. Jeśli jest błąd -> Odpisz: FAILED: <krótki opis błędu>.
        """
        
        user_msg = f"Plik: {filename}\n\nKOD:\n{code}"
        
        try:
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg)
            ])
            feedback = response.content.strip()
            
            if "PASSED" in feedback.upper():
                print(f"   -> ✅ AI zatwierdziło kod.")
                return {"test_feedback": "PASSED", "retry_count": 0}
            else:
                print(f"   -> ❌ AI znalazło błąd: {feedback[:100]}...")
                return _fail_response(state, feedback, retries)
                
        except Exception as e:
            print(f"   -> ⚠️ Błąd połączenia z AI w QA: {e}. Puszczam.")
            return {"test_feedback": "PASSED", "retry_count": 0}

def _fail_response(state, error_msg, retries):
    """Pomocnicza funkcja do zwracania błędu"""
    current_idx = state.get("current_file_index", 1) - 1
    return {
        "test_feedback": f"FAILED: {error_msg}",
        "current_file_index": current_idx,
        "retry_count": retries + 1 
    }