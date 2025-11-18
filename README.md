# 🚀 AgileDev Agents: Autonomiczny Zespół Deweloperski AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.1.0-green)
![Architecture](https://img.shields.io/badge/Architecture-RAG%20%2B%20LangGraph-orange)
![Status](https://img.shields.io/badge/Status-Prototype-yellow)

**AgileDev Agents** to zaawansowany system orkiestracji agentów AI, który symuluje pracę rzeczywistego zespołu deweloperskiego w metodyce Agile. 

Projekt przyjmuje od użytkownika wymagania (jako tekst lub plik PDF), a następnie sieć agentów automatycznie dekomponuje zadania, planuje architekturę, pisze kod i przeprowadza testy. System wykorzystuje **Dynamiczny RAG**, aby "uczyć się" tworzonego kodu na bieżąco.

---

## 🧠 Architektura i Przepływ Pracy

Projekt opiera się na współpracy czterech wyspecjalizowanych agentów.

```mermaid
graph TD
    %% Węzły (Nodes)
    User((Użytkownik))
    PM[Product Manager]
    Arch[Architekt Systemu]
    Dev[Programista]
    QA[QA Reviewer]
    Repo[(Baza Kodu / Git)]
    RAG[(Baza Wiedzy RAG)]

    %% Połączenia (Links)
    User -->|1. PDF/Opis| PM
    PM -->|2. User Stories| Arch
    
    %% Interakcja z RAG
    RAG <.->|3. Context Lookup| Arch
    
    Arch -->|4. Zadania Techniczne| Dev
    Dev -->|5. Kod| QA
    
    %% Pętle zwrotne
    QA -->|6. Testy Failed| Dev
    QA -->|6. Testy Passed| Repo
    
    %% Indeksowanie
    Repo -.->|Indeksowanie| RAG
