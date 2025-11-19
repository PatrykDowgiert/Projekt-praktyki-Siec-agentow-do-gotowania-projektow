from langgraph.graph import StateGraph, END
from core.state import AgentState

# Importy agentów
from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node
from agents.qa_agent import qa_node  # <--- NOWY AGENT

# Funkcja decyzyjna (Router)
def should_continue(state: AgentState):
    feedback = state.get("test_feedback", "")
    iteration = state.get("iteration_count", 0)
    
    # Warunek 1: Jeśli testy przeszły -> KONIEC
    if "PASSED" in feedback:
        return "end"
    
    # Warunek 2: Bezpiecznik - jeśli próbowaliśmy już 3 razy i dalej błędy -> KONIEC (poddajemy się)
    if iteration > 3:
        print("⚠️ [SYSTEM]: Osiągnięto limit poprawek. Kończę pracę.")
        return "end"
    
    # Warunek 3: Jeśli błędy -> WRÓĆ DO PROGRAMISTY
    return "retry"

def run_agile_team():
    # 1. Budowanie Grafu
    workflow = StateGraph(AgentState)

    # Dodawanie węzłów
    workflow.add_node("product_manager", pm_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", coder_node)
    workflow.add_node("qa_engineer", qa_node) # <--- Dodajemy węzeł QA

    # Definiowanie przepływu (Edges)
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", "qa_engineer") # Po kodowaniu idziemy do QA
    
    # ROZGAŁĘZIENIE WARUNKOWE (Conditional Edge)
    workflow.add_conditional_edges(
        "qa_engineer",          # Skąd wychodzimy?
        should_continue,        # Jaka funkcja decyduje?
        {                       # Mapa decyzji
            "end": END,         # Jeśli funkcja zwróci "end" -> Koniec
            "retry": "developer" # Jeśli "retry" -> Wróć do Programisty
        }
    )

    app = workflow.compile()

    # 2. Uruchomienie
    print("🚀 Uruchamiam Zespół Agile AI (z pętlą QA)...")
    
    initial_input = {
        # Zmieńmy wymaganie na trudniejsze, żeby zmusić ich do myślenia
        "requirements": "Napisz klasę w Pythonie 'OllamaClient', która ma metody do listowania modeli i generowania tekstu. Musi używać biblioteki `requests` i obsługiwać błędy połączenia.",
        "plan": [],
        "current_code": "",
        "test_feedback": "",
        "messages": [],
        "iteration_count": 0
    }

    try:
        result = app.invoke(initial_input, {"recursion_limit": 20}) # Zwiększamy limit kroków grafu

        print("\n🏁 --- WYNIK KOŃCOWY (po testach QA) ---")
        print(result["current_code"])
        
        # Zapis
        import os
        if not os.path.exists("workspace"):
            os.makedirs("workspace")
        with open("workspace/wynik.py", "w", encoding="utf-8") as f:
            f.write(result["current_code"])
            print("\n💾 Zapisano w workspace/wynik.py")
            
    except Exception as e:
        print(f"\n❌ Błąd wykonania: {e}")

if __name__ == "__main__":
    run_agile_team()