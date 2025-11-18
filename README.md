Widzę, że parser GitHub/Mermaid jest bardzo wrażliwy na to, jak tekst jest wklejany (skleja ostatnią linię diagramu z następnym nagłówkiem). To frustrujące.

Aby rozwiązać ten problem raz na zawsze i dać Ci działający plik, zamieniłem diagram Mermaid na profesjonalny Diagram ASCII. Jest on "niezniszczalny" – wyświetli się poprawnie w każdym edytorze tekstu, na GitHubie, GitLabie, a nawet w notatniku, i wygląda bardzo "hakersko", co pasuje do narzędzia CLI.

Oto Twoje pancerne README.md. Skopiuj całość:

Markdown

# 🚀 AgileDev Agents: Autonomiczny Zespół Deweloperski AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.1.0-green)
![Architecture](https://img.shields.io/badge/Architecture-RAG%20%2B%20LangGraph-orange)
![Status](https://img.shields.io/badge/Status-Prototype-yellow)

**AgileDev Agents** to zaawansowany system orkiestracji agentów AI, który symuluje pracę rzeczywistego zespołu deweloperskiego w metodyce Agile. 

Projekt przyjmuje od użytkownika wymagania (jako tekst lub plik PDF), a następnie sieć agentów automatycznie dekomponuje zadania, planuje architekturę, pisze kod i przeprowadza testy. System wykorzystuje **Dynamiczny RAG**, aby "uczyć się" tworzonego kodu na bieżąco.

---

## 🧠 Architektura i Przepływ Pracy

System opiera się na cyklicznej współpracy czterech agentów oraz bazy wiedzy.

```text
+-----------------+        +-------------------+
|  Użytkownik     |------->|  Product Manager  |
| (Input: PDF/Txt)|        | (Analiza/Backlog) |
+-----------------+        +-------------------+
                                     |
                                     v
                           +-------------------+      +-----------------+
                           | Architekt Systemu |<---->| Baza Wiedzy RAG |
                           | (Design/Tasks)    |      | (Vector Store)  |
                           +-------------------+      +-----------------+
                                     |                         ^
                                     v                         :
                           +-------------------+               :
          +--------------->|    Programista    |               :
          |                |   (Coding Agent)  |               :
          |                +-------------------+               :
     (Fix Bug)                       |                         :
          |                          v                         :
          |                +-------------------+      (Indeksowanie)
          +----------------|   QA / Reviewer   |               :
             (Test Fail)   | (Tests & Linting) |---------------+
                           +-------------------+      (Test Pass)
                                     |
                                     v
                           +-------------------+
                           |   Repozytorium    |
                           |   (Git / Code)    |
                           +-------------------+
👥 Role Agentów
1. 🕵️ Product Manager (PM)
Cel: Zrozumienie biznesu.

Zadania:

Analiza plików wejściowych (PDF, specyfikacje).

Tworzenie Epików i dekompozycja na User Stories.

Zarządzanie Backlogiem Produktu.

2. 👷 Architekt Systemu (Tech Lead)
Cel: Spójność techniczna.

Zadania:

Analiza User Stories pod kątem technicznym.

Kluczowe: Wykorzystanie RAG do przeszukiwania istniejącego kodu projektu ("Jakie mamy modele?", "Gdzie dodać endpoint?").

Tworzenie precyzyjnych instrukcji implementacyjnych dla programisty.

3. 👨‍💻 Programista (Coder)
Cel: Implementacja.

Zadania:

Pisanie kodu na podstawie specyfikacji od Architekta.

Trzymanie się ściśle narzuconych konwencji i kontekstu.

4. 🐞 QA / Reviewer
Cel: Jakość i stabilność.

Zadania:

Generowanie testów jednostkowych.

Analiza statyczna kodu (linting).

Pętla zwrotna: Jeśli kod zawiera błędy, odsyła go do Programisty z logami błędów do poprawy.

🛠️ Technologie
Projekt zbudowany jest w oparciu o nowoczesny stack AI:

Python 3.10+

LangChain & LangGraph: Do zarządzania stanem i orkiestracji agentów.

RAG (Retrieval-Augmented Generation):

Vector Store: ChromaDB lub FAISS.

Embeddings: OpenAI Embeddings.

LLM: OpenAI GPT-4o (zalecane dla Architekta/Kodera) lub Anthropic Claude 3.5 Sonnet.

Narzędzia: pypdf (ładowanie dokumentów), black/flake8 (analiza kodu).

🚀 Instalacja i Uruchomienie
1. Klonowanie repozytorium
Bash

git clone [https://github.com/twoj-nick/agile-dev-agents.git](https://github.com/twoj-nick/agile-dev-agents.git)
cd agile-dev-agents
2. Utworzenie środowiska wirtualnego
Bash

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
3. Instalacja zależności
Bash

pip install -r requirements.txt
4. Konfiguracja
Utwórz plik .env w głównym katalogu i dodaj klucz API:

Fragment kodu

OPENAI_API_KEY=sk-proj-twoj-klucz-api...
# Opcjonalnie dla lepszego debugowania:
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-twoj-klucz...
5. Użycie
Aby rozpocząć pracę nad nowym projektem na podstawie specyfikacji PDF:

Bash

python main.py --input "docs/specyfikacja_sklepu.pdf" --project_name "SklepInternetowy"
Lub tryb interaktywny:

Bash

python main.py --chat
📂 Struktura Projektu
Plaintext

agile-dev-agents/
├── agents/             # Logika poszczególnych agentów
│   ├── product_manager.py
│   ├── architect.py
│   ├── developer.py
│   └── qa_engineer.py
├── core/               # Konfiguracja RAG i LLM
│   ├── rag_engine.py   # Indeksowanie i wyszukiwanie
│   └── state.py        # Stan LangGraph
├── input/              # Miejsce na pliki PDF/TXT użytkownika
├── workspace/          # Tu agenci generują kod wynikowy
├── main.py             # Punkt wejściowy aplikacji
└── README.md
🗺️ Roadmapa
[ ] Bazowa implementacja 4 agentów w LangGraph.

[ ] System RAG indeksujący kod Pythona w czasie rzeczywistym.

[ ] Obsługa błędów i pętle naprawcze (Self-healing code).

[ ] Interfejs użytkownika w Streamlit.

[ ] Integracja z Dockerem do bezpiecznego uruchamiania kodu.

📄 Licencja
Projekt udostępniony na licencji MIT.
