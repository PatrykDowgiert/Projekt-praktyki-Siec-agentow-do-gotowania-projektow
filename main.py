import os
from langgraph.graph import StateGraph, END
from core.state import AgentState

from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node

# --- LOGIKA PĘTLI (ROUTER) ---
def should_continue_coding(state: AgentState):
    """Sprawdza, czy Programista ma jeszcze pliki do napisania."""
    structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    
    # Ponieważ structure to teraz lista słowników lub napisów (zabezpieczenie),
    # funkcja len() działa tak samo, więc logika się nie zmienia,
    # ale warto upewnić się, że nic tu nie wybuchnie.
    
    if idx < len(structure):
        return "continue"
    else:
        return "end"
        
# --- GŁÓWNA FUNKCJA GENERUJĄCA ---
def run_project_agent(user_prompt, previous_state=None):
    """
    Uruchamia agentów. Przyjmuje user_prompt i opcjonalnie poprzedni stan (do chatu).
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("product_manager", pm_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", coder_node)
    
    # Ścieżka: PM -> Architekt -> Programista
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "developer")
    
    # Pętla Programisty
    workflow.add_conditional_edges(
        "developer",
        should_continue_coding,
        {
            "continue": "developer", # Wróć do pisania kolejnego pliku
            "end": END               # Wszystkie pliki gotowe
        }
    )
    
    app = workflow.compile()
    
    # Jeśli mamy poprzedni stan (kontynuacja rozmowy), używamy go
    if previous_state:
        initial_state = previous_state
        initial_state["requirements"] = user_prompt # Nadpisujemy nowe wymaganie
        # Tutaj można dodać logikę "Refactor", ale dla uproszczenia
        # na razie generujemy od nowa z uwzględnieniem uwag w promptcie
    else:
        initial_state = {
            "requirements": user_prompt,
            "plan": [],
            "file_structure": [],
            "current_file_index": 0,
            "project_files": [],
            "messages": []
        }
    
    print(f"🚀 Start agentów. Prompt: {user_prompt[:50]}...")
    
    # Zwiększony limit rekurencji dla pętli plików
    result = app.invoke(initial_state, {"recursion_limit": 100})
    return result

# --- FUNKCJA ZAPISU ---
def save_files_to_disk(project_name, files):
    base_path = os.path.join("workspace", project_name)
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        
    for f in files:
        full_path = os.path.join(base_path, f['name'])
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(f['content'])
            
    return base_path

