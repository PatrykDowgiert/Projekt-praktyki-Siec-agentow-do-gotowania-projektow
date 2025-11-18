# 🚀 AgileDev Agents: Twój Autonomiczny Zespół Deweloperski AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.1.0-green)
![RAG](https://img.shields.io/badge/Architecture-RAG-orange)
![Status](https://img.shields.io/badge/Status-Prototype-yellow)

**AgileDev Agents** to zaawansowany system orkiestracji agentów AI, który symuluje pracę rzeczywistego zespołu deweloperskiego w metodyce Agile. Projekt przyjmuje wymagania (tekst/PDF), dekomponuje je na zadania i automatycznie generuje, testuje oraz integruje kod, wykorzystując dynamiczny RAG (Retrieval-Augmented Generation) na bazie kodu.

---

## 🧠 Architektura Systemu

Projekt opiera się na współpracy czterech wyspecjalizowanych agentów. Każdy z nich pełni unikalną rolę w procesie wytwarzania oprogramowania (SDLC).

```mermaid
graph TD
    User((Użytkownik)) -->|PDF/Wymagania| PM[🕵️ Product Manager]
    PM -->|User Stories| Arch[👷 Architekt Systemu]
    Arch -->|Zadania Techniczne + RAG| Dev[👨‍💻 Programista]
    Dev -->|Kod| QA[🐞 QA / Reviewer]
    QA -->|Pass| Repo[(Baza Kodu / Git)]
    QA -->|Fail| Dev
    Repo -.->|Indeksowanie| RAG{Dynamiczny RAG}
    RAG -.-> Arch
👥 Zespół Agentów (Roles)
1. 🕵️ Product Manager (PM)
Rola: Punkt kontaktu z użytkownikiem.

Zadanie: Analizuje pliki wejściowe (PDF, specyfikacje), tworzy Epiki i User Stories, zarządza Backlogiem Produktu.

Decyzje: Priorytetyzacja zadań i akceptacja końcowa.

2. 👷 Architekt Systemu (Tech Lead)
Rola: Mózg operacji technicznych.

Zadanie: Przekłada User Stories na konkretne zadania techniczne.

Supermoc (RAG): Przeszukuje całą istniejącą bazę kodu, aby zapewnić, że nowe funkcje są zgodne z istniejącą architekturą i konwencjami.

3. 👨‍💻 Programista (Coder)
Rola: Wykonawca.

Zadanie: Pisze kod na podstawie specyfikacji od Architekta.

Działanie: Implementuje funkcje, trzymając się ściśle kontekstu dostarczonego przez system RAG.

4. 🐞 QA / Reviewer
Rola: Strażnik jakości.

Zadanie: Pisze testy, wykonuje analizę statyczną kodu i przeprowadza Code Review.

Decyzje: Jeśli kod nie spełnia standardów lub testy nie przechodzą, cofa zadanie do Programisty.

⭐ Kluczowe Funkcjonalności
📄 Analiza Dokumentacji: Wczytywanie plików PDF, TXT i MD jako źródła wiedzy o projekcie.

🔄 Dynamiczny RAG na Kodzie: System nie tylko czyta dokumentację, ale na bieżąco indeksuje nowo powstały kod. Architekt zawsze "widzi" aktualny stan repozytorium.

⚙️ Pętla Zwrotna (Feedback Loop): Automatyczna korekta błędów – jeśli testy QA zawiodą, agent programista otrzymuje logi błędów i poprawia kod.

📝 Generowanie Raportów: PM dostarcza podsumowanie wykonanych prac w formacie zrozumiałym dla biznesu.

🛠️ Tech Stack
Język: Python 3.11+

Orkiestracja: LangChain / LangGraph

Baza Wektorowa: ChromaDB / FAISS (do przechowywania wiedzy o kodzie)

LLM: OpenAI GPT-4o / Claude 3.5 Sonnet (konfigurowalne)

Narzędzia: PyPDF (obsługa PDF), Black/Flake8 (lintery), Pytest (testy)
