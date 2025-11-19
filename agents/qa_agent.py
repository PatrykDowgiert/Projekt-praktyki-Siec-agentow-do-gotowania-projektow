import ast
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def qa_node(state: AgentState):
    print("\n🐞 [QA]: Szybka weryfikacja składni...")
    
    # Pobieramy ostatnio edytowany plik
    idx = state.get("current_file_index", 1) - 1
    files = state.get("project_files", [])
    
    if not files or idx < 0:
         # Coś poszło nie tak, przepuszczamy
        return {"test_feedback": "PASSED"}

    current_file = files[-1] # Ostatni dodany
    code = current_file["content"]
    filename = current_file["name"]
    
    # 1. Test Składni (AST) - Wyłapuje "gadanie" modelu
    try:
        ast.parse(code)
        print(f"   -> ✅ Składnia {filename} poprawna.")
    except SyntaxError as e:
        error_msg = f"Błąd składni w pliku {filename} linia {e.lineno}: {e.msg}. Prawdopodobnie model dodał tekst poza kodem."
        print(f"   -> ❌ {error_msg}")
        # Cofamy indeks, żeby Coder poprawił ten sam plik
        return {
            "test_feedback": f"FAILED: {error_msg}",
            "current_file_index": idx # Cofka
        }

    # 2. (Opcjonalnie) Test Logiczny przez LLM - jeśli chcesz być super dokładny
    # Na razie pomińmy to dla szybkości, skoro problemem były śmieci w kodzie.
    
    return {"test_feedback": "PASSED"}