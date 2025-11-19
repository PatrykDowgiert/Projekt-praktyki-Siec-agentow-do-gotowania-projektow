import os
from langgraph.graph import StateGraph, END
from core.state import AgentState

from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node
from agents.qa_agent import qa_node # <--- Importujemy QA

# --- FUNKCJE POMOCNICZE ---
def save_files(project_name, files):
    base_path = os.path.join("workspace", project_name)
    if not os.path.exists(base_path): os.makedirs(base_path)
    print(f"\n💾 Zapisuję w: {base_path}")
    for f in files:
        full_path = os.path.join(base_path, f['name'])
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(f['content'])
    return base_path

# --- ROUTER QA ---
def route_after_qa(state: AgentState):
    feedback = state.get("test_feedback", "")
    structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    
    if "FAILED" in feedback:
        print("   -> 🔙 Wróc do Codera (Poprawka)")
        return "developer" # Wracamy poprawić TEN SAM plik
    
    # Jeśli PASSED, sprawdzamy czy są kolejne pliki
    if idx < len(structure):
        return "developer" # Idziemy do NASTĘPNEGO pliku
    else:
        return "end" # Koniec pracy

def generate_project(user_prompt):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("product_manager", pm_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", coder_node)
    workflow.add_node("qa", qa_node) # <--- Węzeł QA
    
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "developer")
    
    # Developer zawsze idzie do QA sprawdzić to co napisał
    workflow.add_edge("developer", "qa")
    
    # QA decyduje: poprawiamy czy idziemy dalej?
    workflow.add_conditional_edges(
        "qa",
        route_after_qa,
        {
            "developer": "developer",
            "end": END
        }
    )
    
    app = workflow.compile()
    
    initial_state = {
        "requirements": user_prompt,
        "plan": [],
        "file_structure": [],
        "project_files": [],
        "messages": [],
        "current_file_index": 0
    }
    
    print(f"🚀 Start: {user_prompt[:40]}...")
    try:
        result = app.invoke(initial_state, {"recursion_limit": 100})
        return result.get("project_files", [])
    except Exception as e:
        return {"error": str(e)}