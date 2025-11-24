import os
import traceback
from langgraph.graph import StateGraph, END
from core.state import AgentState

# Importy agentów
from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node
from agents.qa_agent import qa_node

# --- FUNKCJE POMOCNICZE ---
def save_files_to_disk(project_name, files):
    base_path = os.path.join("workspace", project_name)
    if not os.path.exists(base_path): os.makedirs(base_path)
    print(f"\n💾 Zapisuję projekt w: {base_path}")
    
    if not files: return base_path

    for file_data in files:
        if file_data is None or not isinstance(file_data, dict): continue
        file_name = file_data.get("name")
        content = file_data.get("content")
        
        if not file_name or not content: continue
        
        try:
            full_path = os.path.join(base_path, file_name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"⚠️ Błąd zapisu {file_name}: {e}")
            
    return base_path

# --- ROUTER ---
def route_after_qa(state: AgentState):
    feedback = state.get("test_feedback", "")
    structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    
    if "FAILED" in feedback:
        return "developer"
    
    if structure is None: return "end"
    if idx < len(structure):
        return "developer"
    else:
        return "end"

# --- SILNIK Z PASEKIEM PROGRESU ---
def run_project_agent(user_prompt, previous_state=None, progress_bar=None, status_text=None):
    """
    Główna funkcja, teraz obsługuje strumieniowanie (stream) dla paska postępu.
    """
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
        if "project_files" in initial_state and initial_state["project_files"]:
            initial_state["project_files"] = [f for f in initial_state["project_files"] if f is not None]
    else:
        initial_state = {
            "requirements": user_prompt,
            "plan": [],
            "file_structure": [],
            "project_files": [],
            "messages": [],
            "current_file_index": 0,
            "test_feedback": "",
            "retry_count": 0
        }
    
    print(f"🚀 Start: {user_prompt[:30]}...")
    
    final_state = initial_state

    try:
        # UŻYWAMY .stream() ZAMIAST .invoke()
        # To pozwala nam reagować na każdy krok agenta
        step_count = 0
        
        for event in app.stream(initial_state, {"recursion_limit": 150}):
            # event to słownik np. {'product_manager': {stan...}}
            
            # Pobieramy nazwę węzła i nowy stan
            node_name = list(event.keys())[0]
            state = event[node_name]
            final_state = state # Aktualizujemy stan końcowy
            
            # --- AKTUALIZACJA UI (PASEK POSTĘPU) ---
            if progress_bar and status_text:
                
                if node_name == "product_manager":
                    progress_bar.progress(10, "🕵️ PM: Analiza wymagań zakończona.")
                    
                elif node_name == "architect":
                    files_count = len(state.get("file_structure", []))
                    progress_bar.progress(20, f"👷 Architekt: Zaplanowano {files_count} plików.")
                    
                elif node_name == "developer":
                    # Obliczamy postęp na podstawie liczby plików
                    files = state.get("file_structure", [])
                    idx = state.get("current_file_index", 0)
                    total = len(files) if files else 1
                    
                    # Programista pracuje od 20% do 90% paska
                    # np. 2/4 pliki -> 50% pracy dev -> 20 + (0.5 * 70) = 55% ogółu
                    percent = 20 + int((idx / total) * 70)
                    percent = min(percent, 90) # Nie przekraczamy 90% przed końcem
                    
                    filename = files[idx-1]["filename"] if idx > 0 and isinstance(files[idx-1], dict) else "plik"
                    progress_bar.progress(percent, f"👨‍💻 Programista: Utworzono {filename} ({idx}/{total})")
                    
                elif node_name == "qa":
                    feedback = state.get("test_feedback", "OK")
                    if "FAILED" in feedback:
                        status_text.warning(f"🐞 QA: Znaleziono błąd. Poprawiamy...")
                    else:
                        status_text.success("🐞 QA: Kod zatwierdzony.")

        # Koniec pętli = 100%
        if progress_bar:
            progress_bar.progress(100, "✅ Gotowe! Projekt wygenerowany.")
            
        # Filtrowanie wyników
        clean_files = [f for f in final_state.get("project_files", []) if f is not None]
        final_state["project_files"] = clean_files
        return final_state
        
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")
        traceback.print_exc()
        raise e

if __name__ == "__main__":
    try:
        prompt = input("Prompt: ")
        res = run_project_agent(prompt)
    except:
        pass