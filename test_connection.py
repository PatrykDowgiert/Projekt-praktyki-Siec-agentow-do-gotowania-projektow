from config_factory import get_llm

def test_ollama():
    print("--- Rozpoczynam test połączenia z korporacyjną Ollamą ---")
    
    try:
        # Pobieramy model kodera (qwen3-coder)
        llm = get_llm(model_role="coder")
        
        print("Wysłanie zapytania testowego...")
        response = llm.invoke("Napisz funkcję w Pythonie, która dodaje dwie liczby.")
        
        print("\n--- Odpowiedź modelu ---")
        print(response.content)
        print("\n--- SUKCES! Połączenie działa. ---")
        
    except Exception as e:
        print(f"\n--- BŁĄD POŁĄCZENIA ---")
        print(f"Treść błędu: {e}")
        print("Sprawdź plik .env, token oraz czy jesteś w VPN (jeśli wymagany).")

if __name__ == "__main__":
    test_ollama()