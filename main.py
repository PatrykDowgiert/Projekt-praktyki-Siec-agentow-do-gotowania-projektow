import os
import traceback
from langgraph.graph import StateGraph, END
from core.state import AgentState

from agents.pm_agent import pm_node
from agents.architect_agent import architect_node
from agents.coder_agent import coder_node
from agents.qa_agent import qa_node

def save_files_to_disk(project_name, files):
    base_path = os.path.join("workspace", project_name)
    if not os.path.exists(base_path): os.makedirs(base_path)
    print(f"\n💾 Zapisuję projekt w: {base_path}")
    
    if not files: 
        print("⚠️ Brak plików do zapisania (lista pusta).")
        return base_path

    saved_count = 0
    for file_data in files:
        if not file_data or not isinstance(file_data, dict): continue
        file_name = file_data.get("name")
        content = file_data.get("content")
        
        if not file_name or not content: continue
        
        try:
            full_path = os.path.join(base_path, file_name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            saved_count += 1
        except Exception as e:
            print(f"⚠️ Błąd zapisu {file_name}: {e}")
            
    print(f"✅ Zapisano łącznie {saved_count} plików.")
    return base_path

def route_after_qa(state: AgentState):
    feedback = state.get("test_feedback", "")
    structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    
    if "FAILED" in feedback: return "developer"
    if not structure: return "end"
    if idx < len(structure): return "developer"
    else: return "end"

def run_project_agent(user_prompt, previous_state=None, progress_bar=None, status_text=None):
    workflow = StateGraph(AgentState)
    workflow.add_node("product_manager", pm_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", coder_node)
    workflow.add_node("qa", qa_node)
    
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", "qa")
    workflow.add_conditional_edges("qa", route_after_qa, { "developer": "developer", "end": END })
    
    app = workflow.compile()
    
    if previous_state:
        initial_state = previous_state.copy() # Kopia dla bezpieczeństwa
        initial_state["requirements"] = user_prompt
        initial_state["test_feedback"] = ""
        # Czyścimy None z listy plików
        if initial_state.get("project_files"):
            initial_state["project_files"] = [f for f in initial_state["project_files"] if f]
    else:
        initial_state = {
            "requirements": user_prompt, "plan": [], "file_structure": [],
            "project_files": [], "messages": [], "current_file_index": 0,
            "test_feedback": "", "retry_count": 0
        }
    
    print(f"🚀 Start: {user_prompt[:30]}...")
    
    # Kopia stanu początkowego
    final_state = initial_state.copy()

    try:
        for event in app.stream(initial_state, {"recursion_limit": 150}):
            node_name = list(event.keys())[0]
            state = event[node_name]
            
            # --- KLUCZOWA POPRAWKA ---
            # Zamiast nadpisywać (final_state = state), AKTUALIZUJEMY słownik.
            # Dzięki temu, gdy QA zwróci tylko feedback, nie skasuje plików Codera.
            final_state.update(state)
            # -------------------------
            
            # Logika paska postępu
            if progress_bar and status_text:
                if node_name == "product_manager":
                    progress_bar.progress(10, "🕵️ PM: Analiza zakończona.")
                elif node_name == "architect":
                    struct = state.get("file_structure", [])
                    if not struct: struct = []
                    progress_bar.progress(20, f"👷 Architekt: {len(struct)} plików.")
                elif node_name == "developer":
                    files = state.get("file_structure", [])
                    idx = state.get("current_file_index", 0)
                    total = len(files) if files else 1
                    percent = 20 + int((idx / total) * 70)
                    percent = min(percent, 90)
                    
                    current_file = "plik"
                    if files and idx > 0 and (idx-1) < len(files):
                        item = files[idx-1]
                        if item and isinstance(item, dict):
                            current_file = item.get("filename", "plik")
                    
                    progress_bar.progress(percent, f"👨‍💻 Dev: {current_file} ({idx}/{total})")
                elif node_name == "qa":
                    if "FAILED" in state.get("test_feedback", ""):
                        status_text.warning(f"🐞 QA: Poprawka...")
                    else:
                        status_text.success("🐞 QA: OK.")

        if progress_bar: progress_bar.progress(100, "✅ Gotowe!")
        
        # Ostatnie sprawdzenie przed zwrotem
        clean_files = [f for f in final_state.get("project_files", []) if f]
        print(f"🔍 DEBUG [Koniec]: W finalnym stanie jest {len(clean_files)} plików.")
        
        final_state["project_files"] = clean_files
        return final_state
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        traceback.print_exc()
        return final_state

if __name__ == "__main__":
    try:
        prompt = input("Prompt: ")
        run_project_agent(prompt)
    except: pass