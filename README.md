# 🚀 AgileDev Agents: Autonomiczny Zespół Deweloperski AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.1.0-green?style=for-the-badge&logo=chainlink&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-RAG%20%2B%20LangGraph-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Prototype-yellow?style=for-the-badge)

**AgileDev Agents** to system orkiestracji agentów AI, który symuluje pracę rzeczywistego zespołu deweloperskiego (Scrum/Agile). 

Projekt przyjmuje wymagania (tekst lub PDF), a sieć agentów automatycznie:
1. Analizuje zadania biznesowe.
2. Projektuje rozwiązania techniczne w oparciu o istniejący kod (RAG).
3. Pisze kod.
4. Testuje i naprawia błędy przed zatwierdzeniem.

---

## 🧠 Architektura Systemu

System wykorzystuje **cykliczny graf agentów** (LangGraph) oraz **wspólną pamięć** (RAG), aby zachować spójność projektu.

~~~text
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
                           |   (Workspace)     |
                           +-------------------+
~~~

---

## 👥 Role w Zespole AI

### 🕵️ Product Manager (PM)
* **Rola:** Zarządzanie produktem
* **Zadania:** Analiza wymagań, tworzenie User Stories, priorytetyzacja backlogu.

### 👷 Architekt Systemu (Tech Lead)
* **Rola:** Nadzór techniczny
* **Zadania:** Planowanie architektury, podział na pod-zadania.
* **Supermoc:** Analiza istniejącego kodu przez RAG ("wiem, co już mamy w systemie").

### 👨‍💻 Programista (Coder)
* **Rola:** Wykonawca
* **Zadania:** Generowanie czystego kodu Python zgodnie z wytycznymi Architekta.

### 🐞 QA / Reviewer
* **Rola:** Kontrola jakości
* **Zadania:** Pisanie testów (`pytest`), analiza statyczna kodu, odrzucanie błędnych rozwiązań (Feedback Loop).

---

## 📂 Struktura Projektu

~~~text
agile-dev-agents/
├── agents/             # Mózgi poszczególnych agentów
│   ├── product_manager.py
│   ├── architect.py
│   ├── developer.py
│   └── qa_engineer.py
├── core/               # Rdzeń systemu
│   ├── rag_engine.py   # Silnik RAG (ChromaDB + Embeddings)
│   └── state.py        # Definicja stanu globalnego (State)
├── input/              # Folder na dokumentację wejściową (PDF)
├── workspace/          # Folder roboczy (tu powstaje kod wynikowy)
├── main.py             # Punkt startowy aplikacji
└── requirements.txt    # Zależności
~~~

---

## 🚀 Instalacja i Uruchomienie

### 1. Klonowanie
~~~bash
git clone [https://github.com/twoj-nick/agile-dev-agents.git](https://github.com/twoj-nick/agile-dev-agents.git)
cd agile-dev-agents
~~~

### 2. Środowisko wirtualne
~~~bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate
~~~

### 3. Instalacja zależności
~~~bash
pip install -r requirements.txt
~~~

### 4. Konfiguracja API
Utwórz plik `.env` w głównym katalogu i wklej swój klucz OpenAI:
~~~env
OPENAI_API_KEY=sk-proj-twoj-klucz-api...
~~~

### 5. Uruchomienie
Wrzuć plik z wymaganiami (np. `specyfikacja.pdf`) do folderu `input/` i uruchom:

~~~bash
python main.py
~~~

---

## 🛠️ Stack Technologiczny

* **Język:** Python 3.10+
* **Orkiestracja:** LangChain + LangGraph
* **Pamięć (RAG):** ChromaDB
* **LLM:** OpenAI GPT-4o
* **Narzędzia:** PyPDF, Black (formatter), Pytest

---

## 📄 Licencja
MIT
