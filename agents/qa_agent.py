from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def qa_node(state: AgentState):
    """
    Rola: QA Engineer
    Zadanie: Sprawdzenie jakości kodu (Static Analysis / Code Review).
    """
    print("\n🐞 [QA]: Sprawdzam kod...")
    
    code = state.get("current_code", "")
    requirements = state.get("requirements", "")
    
    # Używamy modelu kodera, bo on najlepiej widzi błędy w składni
    llm = get_llm(model_role="coder")
    
    system_prompt = """Jesteś surowym inżynierem QA (Quality Assurance).
    Twoim zadaniem jest przeanalizowanie kodu Pythona pod kątem błędów składniowych, logicznych i bezpieczeństwa.
    
    Zasady oceniania:
    1. Jeśli kod wygląda poprawnie i spełnia wymagania -> Odpowiedz słowem: PASSED.
    2. Jeśli kod ma błędy, braki importów lub jest niebezpieczny -> Odpowiedz słowem: FAILED, a następnie w nowej linii opisz dokładnie co trzeba poprawić.
    
    Format odpowiedzi:
    PASSED
    (lub)
    FAILED
    Lista błędów:
    - Błąd 1...
    - Błąd 2...
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"WYMAGANIA:\n{requirements}\n\nKOD DO SPRAWDZENIA:\n{code}")
    ]
    
    response = llm.invoke(messages)
    feedback = response.content
    
    # Zwiększamy licznik iteracji (żeby nie utknąć w pętli w nieskończoność)
    iteration = state.get("iteration_count", 0) + 1
    
    if "PASSED" in feedback:
        print("🐞 [QA]: Testy zaliczone ✅")
    else:
        print(f"🐞 [QA]: Znaleziono błędy ❌ (Iteracja {iteration})")
        # print(f"Feedback: {feedback}") # Opcjonalnie wypisz szczegóły
    
    return {
        "test_feedback": feedback,
        "iteration_count": iteration,
        "messages": [response]
    }