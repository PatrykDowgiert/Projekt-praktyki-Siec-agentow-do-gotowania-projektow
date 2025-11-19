from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm
# from core.rag_engine import ProjectKnowledgeBase # RAG opcjonalny

def architect_node(state: AgentState):
    print("\n👷 [Architekt]: Projektuję strukturę plików...")
    
    requirements = state.get("requirements", "")
    plan_pm = state.get("plan", [])[-1]
    
    llm = get_llm(model_role="coder") # Coder model jest lepszy w strukturach technicznych
    
    system_prompt = """Jesteś Głównym Architektem. 
    Na podstawie wymagań, zaprojektuj strukturę plików dla projektu Python.
    
    Wymagania:
    1. Zawsze uwzględnij 'main.py', 'requirements.txt' i 'README.md'.
    2. Podziel kod na logiczne moduły.
    3. Wypisz TYLKO listę plików, każdy w nowej linii.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Wymagania: {requirements}\nPlan PM: {plan_pm}")
    ]
    
    response = llm.invoke(messages)
    # Zamieniamy odpowiedź tekstową na listę plików (usuwamy puste linie)
    file_list = [f.strip() for f in response.content.split('\n') if f.strip() and not f.startswith('#')]
    
    print(f"👷 [Architekt]: Zaplanowane pliki:\n" + "\n".join(f"   - {f}" for f in file_list))
    
    return {
        "file_structure": file_list,
        "messages": [response]
    }