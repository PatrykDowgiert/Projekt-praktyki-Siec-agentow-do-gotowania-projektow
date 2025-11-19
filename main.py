from langgraph.graph import StateGraph, END
from core.state import AgentState

# Importy naszych agentów (węzłów)
from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node

def run_agile_team():
    # 1. Budowanie Grafu
    workflow = StateGraph(AgentState)

    # Dodawanie węzłów (Nodes)
    workflow.add_node("product_manager", pm_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", coder_node)

    # Definiowanie krawędzi (Edges) - przepływ pracy
    # Start -> PM -> Architekt -> Programista -> Koniec
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", END)

    # Kompilacja grafu
    app = workflow.compile()

    # 2. Uruchomienie procesu
    print("🚀 Uruchamiam Zespół Agile AI...")
    
    # Przykładowe zadanie na start
    initial_input = {
        "requirements": "Stwórz skrypt w Pythonie, który łączy się z API Ollamy i wypisuje listę dostępnych modeli w konsoli.",
        "plan": [],
        "current_code": "",
        "messages": [],
        "iteration_count": 0
    }

    # app.invoke uruchamia graf
    result = app.invoke(initial_input)

    print("\n🏁 --- WYNIK KOŃCOWY ---")
    print(result["current_code"])
    
    # Zapis wyniku do pliku
    import os
    if not os.path.exists("workspace"):
        os.makedirs("workspace")
        
    with open("workspace/wynik.py", "w", encoding="utf-8") as f:
        f.write(result["current_code"])
        print("\n💾 Zapisano kod w folderze workspace/wynik.py")

if __name__ == "__main__":
    run_agile_team()