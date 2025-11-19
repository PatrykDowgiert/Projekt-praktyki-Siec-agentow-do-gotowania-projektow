from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def pm_node(state: AgentState):
    print("\n🕵️  [PM]: Analizuję wymagania (TRYB: Ścisły)...")
    
    requirements = state.get("requirements", "")
    
    llm = get_llm(model_role="pm")
    
    system_prompt = """Jesteś Product Managerem, który ceni minimalizm (MVP - Minimum Viable Product).
    
    TWOJE ZADANIE:
    Przeanalizuj wymagania użytkownika i stwórz plan zadań.
    
    ZASADY KRYTYCZNE:
    1. TRZYMAJ SIĘ TYLKO TEGO, CO NAPISAŁ UŻYTKOWNIK.
    2. ZAKAZ WYMYŚLANIA DODATKOWYCH FUNKCJI (Scope Creep).
    3. Jeśli użytkownik prosi o grę konsolową -> NIE dodawaj Django/Flask/Web.
    4. Jeśli użytkownik prosi o prosty skrypt -> NIE planuj architektury mikroserwisów.
    5. Bądź konkretny i zwięzły.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania użytkownika: {requirements}")
    ]
    
    response = llm.invoke(messages)
    plan_content = response.content
    
    print(f"🕵️  [PM]: Plan gotowy.")
    
    return {
        "plan": [plan_content],
        "messages": [response]
    }