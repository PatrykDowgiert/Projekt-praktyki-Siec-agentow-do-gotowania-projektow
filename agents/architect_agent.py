from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm
from core.rag_engine import ProjectKnowledgeBase

def architect_node(state: AgentState):
    """
    Rola: Architekt Systemu
    Zadanie: Doprecyzowanie planu PM-a o szczegóły techniczne na podstawie bazy wiedzy (RAG).
    """
    print("\n👷 [Architekt]: Konsultuję bazę wiedzy i projektuję rozwiązanie...")
    
    plan = state.get("plan", [])
    # Jeśli plan jest listą, bierzemy ostatni element (najnowszy plan)
    current_plan = plan[-1] if plan else "Brak planu."
    
    # 1. Użycie RAG - szukamy kontekstu dla tego planu
    kb = ProjectKnowledgeBase()
    # Szukamy w bazie wiedzy czegoś, co pasuje do planu (np. "jak używać autoryzacji", "struktura projektu")
    context_docs = kb.search(query=current_plan[:200], k=3) # Skracamy query dla wydajności
    
    context_text = "\n".join([doc.page_content for doc in context_docs])
    
    if not context_text:
        context_text = "Brak wcześniejszej dokumentacji w bazie wiedzy."
        print("👷 [Architekt]: Brak danych w RAG. Tworzę rozwiązanie od zera.")
    else:
        print("👷 [Architekt]: Znalazłem powiązane fragmenty w dokumentacji (RAG).")

    # 2. Wywołanie LLM (Architekta)
    llm = get_llm(model_role="coder") # Architekt też powinien znać się na kodzie
    
    system_prompt = f"""Jesteś Głównym Architektem Oprogramowania.
    Otrzymałeś plan zadań od Product Managera.
    Twoim zadaniem jest przygotowanie WYTYCZNYCH TECHNICZNYCH dla programisty.
    
    KONTEKST Z BAZY WIEDZY (RAG):
    {context_text}
    
    Instrukcja:
    1. Przeanalizuj plan PM-a.
    2. Wykorzystaj kontekst z RAG (np. istniejące biblioteki, konwencje), aby rozwiązanie było spójne.
    3. Wypisz konkretne kroki implementacyjne (jakie pliki utworzyć, jakich bibliotek użyć).
    4. Bądź zwięzły i techniczny.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"PLAN PM-a:\n{current_plan}")
    ]
    
    response = llm.invoke(messages)
    tech_guidelines = response.content
    
    # Aktualizujemy plan o wytyczne techniczne (nadpisujemy lub dodajemy)
    # W tym prostym modelu po prostu dodajemy to jako kolejny element planu
    return {
        "plan": [tech_guidelines],
        "messages": [response]
    }