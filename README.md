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
