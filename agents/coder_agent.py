from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from config_factory import get_llm

def coder_node(state: AgentState):
    file_structure = state.get("file_structure", [])
    idx = state.get("current_file_index", 0)
    existing_files = state.get("project_files", [])
    
    # Zabezpieczenie przed wyjściem poza zakres
    if idx >= len(file_structure):
        return {}

    current_filename = file_structure[idx]
    print(f"\n👨‍💻 [Coder]: Piszę plik {idx+1}/{len(file_structure)}: {current_filename}...")
    
    # Budujemy kontekst (pokazujemy mu kod plików, które już stworzył)
    context_files = ""
    for f in existing_files:
        context_files += f"\n--- PLIK: {f['name']} ---\n{f['content']}\n"
    
    llm = get_llm(model_role="coder")
    
    system_prompt = f"""Jesteś Ekspertem Python. Piszesz kod projektu plik po pliku.
    
    TWOJE ZADANIE:
    Napisz zawartość pliku: '{current_filename}'.
    
    KONTEKST (Pliki już utworzone):
    {context_files if context_files else "To pierwszy plik."}
    
    WYMAGANIA:
    1. Zwróć TYLKO kod tego jednego pliku.
    2. Nie używaj znaczników markdown (```python), jeśli to możliwe.
    3. Pamiętaj o importach z plików, które masz w kontekście.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Napisz kod dla: {current_filename}")
    ]
    
    response = llm.invoke(messages)
    code = response.content.replace("```python", "").replace("```", "").strip()
    
    # Dodajemy nowy plik do listy
    new_file = {"name": current_filename, "content": code}
    updated_files = existing_files + [new_file]
    
    return {
        "project_files": updated_files,       # Aktualizujemy listę plików
        "current_file_index": idx + 1,        # Przesuwamy licznik dalej
        "messages": [response]
    }