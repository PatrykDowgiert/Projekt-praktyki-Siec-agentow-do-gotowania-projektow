import os
import traceback # Do śledzenia błędów
from langgraph.graph import StateGraph, END
from core.state import AgentState

# Importy agentów
from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node
from agents.qa_agent import qa_node

# --- PANCERNA FUNKCJA ZAPISU ---
def save_files_to_disk(project_name, files):
    """
    Zapisuje listę plików na dysk. Odporna na błędy NoneType.
    """
    base_path = os.path.join("workspace", project_name)
    
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        
    print(f"\n💾 Zapisuję projekt w: {base_path}")
    
    if not files:
        print("⚠️ Brak plików do zapisania.")
        return base_path

    for file_data in files:
        # --- OTO POPRAWKA KTÓRA NAPRAWIA TWÓJ BŁĄD ---
        if file_data is None:
            continue
        if not isinstance(file_data, dict):
            continue
        # ---------------------------------------------

        file_name = file_data.get("name")
        content = file_data.get("content")
        
        if not file_name or not content:
            continue
        
        try:
            full_path = os.path.join(base_path, file_name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
                print(f"   -> Utworzono: {file_name}")
        except Exception as e:
            print(f"⚠️ Błąd przy zapisie pliku {file_name}: {e}")
            
    return base_path

# --- ROUTER ---
def route_after_qa(state: AgentState):
    feedback = state.get("test_feedback", "")
    structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    
    if "FAILED" in feedback:
        print("   -> 🔙 QA: Błąd wykryty. Poprawka.")
        return "developer"
    
    # Zabezpieczenie przed None w strukturze
    if structure is None: 
        return "end"
        
    if idx < len(structure):
        return "developer"
    else:
        return "end"

# --- SILNIK ---
def run_project_agent(user_prompt, previous_state=None):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("product_manager", pm_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", coder_node)
    workflow.add_node("qa", qa_node)
    
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", "qa")
    
    workflow.add_conditional_edges(
        "qa",
        route_after_qa,
        { "developer": "developer", "end": END }
    )
    
    app = workflow.compile()
    
    # Inicjalizacja stanu
    if previous_state:
        initial_state = previous_state
        initial_state["requirements"] = user_prompt
        initial_state["test_feedback"] = "" 
        # Czyścimy ewentualne None z listy plików w pamięci, żeby nie psuły procesu
        if "project_files" in initial_state and initial_state["project_files"]:
            initial_state["project_files"] = [f for f in initial_state["project_files"] if f is not None]
    else:
        # Nowy projekt
        initial_state = {
            "requirements": user_prompt,
            "plan": [],
            "file_structure": [],
            "project_files": [],
            "messages": [],
            "current_file_index": 0,
            "test_feedback": "",
            "retry_count": 0  # <--- DODAJ TO
        }
    
    print(f"🚀 Start: {user_prompt[:30]}...")
    
    
    try:
        result = app.invoke(initial_state, {"recursion_limit": 150})
        # Ostatnie filtrowanie wyników przed zwróceniem
        clean_files = [f for f in result.get("project_files", []) if f is not None]
        result["project_files"] = clean_files
        return result
        
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")