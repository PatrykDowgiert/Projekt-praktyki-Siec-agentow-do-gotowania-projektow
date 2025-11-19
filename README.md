# 🚀 AgileDev Agents

<div align="center">

<img src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=1200&auto=format&fit=crop" alt="Banner" width="100%" style="border-radius: 10px;" />

<br><br>

<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/LangChain-0.1.0-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain" />
<img src="https://img.shields.io/badge/Architecture-RAG-FF4B4B?style=for-the-badge&logo=google-cloud&logoColor=white" alt="RAG" />

<br>

### 🤖 Autonomiczny Zespół Deweloperski AI
**Od pliku PDF do działającego kodu – bez mikromanagementu.**

[Instalacja](#-instalacja) • [Jak to działa](#-architektura) • [Roadmapa](#-roadmapa)

</div>

---

## 🧠 Architektura Systemu

Zamiast prostego chatbota, system wykorzystuje sieć agentów wymieniających się zadaniami. Każdy agent ma dostęp do **wspólnej pamięci (RAG)**.

<div align="center">
<img src="https://mermaid.ink/img/pako:eNp1kcFqwzAMhl8l6NRC-wI5jD2MncZ22G2H4iSuEws2trOylL57TjottB12iP-_P9k6oRkz1Ciafm_8iM-FPTjeL5fF8rwsL9fF8nI1fP6Y4_1yNf_6sB_2w9H_j2_71_3h5fvHdv_y9bT9sP_Y7oaj4T1mR5M11JAWc2_cgIqW7z0a7bT7o44adW-8gYgO9S9qS4s5q3FoSMPAFW0dGjK0rL2BiI6N7zBrQ4u5beKgIQ9Dk7V1aCjQqvYGIno0vqOsDS3m1omDhjwNXdbWoaFA69obiOjZ-I6yNrSYOyYOjXka-qytQ0OFdja8_wD-rWwR?type=png" alt="Architektura Agentów" width="600" />
</div>

---

## 👥 Twój Zespół AI

| Avatar | Agent | Rola i Odpowiedzialność |
| :---: | :--- | :--- |
| <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/People/Detective.png" width="35" /> | **Product Manager** | **Analiza Biznesowa**<br>Czyta PDF, tworzy User Stories i zarządza backlogiem. |
| <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/People/Construction%20Worker.png" width="35" /> | **Architekt** | **Tech Lead**<br>Używa RAG, by sprawdzić stary kod i zaplanować nowy. |
| <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/People/Technologist.png" width="35" /> | **Programista** | **Coding**<br>Pisze kod Python zgodnie z wytycznymi Architekta. |
| <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Lady%20Beetle.png" width="35" /> | **QA Tester** | **Quality Assurance**<br>Pisze testy, uruchamia je i zwraca błędy do poprawy. |

---

## 📂 Struktura Projektu

```text
agile-dev-agents/
├── 🧠 agents/           # Logika "mózgów" agentów
├── ⚙️ core/             # Silnik RAG i stan
├── 📥 input/            # Tu wrzucasz PDF z pomysłem
├── 🔨 workspace/        # Tu powstaje Twój kod
└── 📜 main.py           # Plik startowy
````

-----

## 🚀 Instalacja

1.  **Pobierz projekt:**

    ```bash
    git clone [https://github.com/twoj-nick/agile-dev-agents.git](https://github.com/twoj-nick/agile-dev-agents.git)
    ```

2.  **Zainstaluj zależności:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Ustaw klucz API:**
    Stwórz plik `.env` i wpisz: `OPENAI_API_KEY=sk-...`

4.  **Uruchom:**

    ```bash
    python main.py
    ```

-----

<div align="center">

Projekt stworzony z pasji do AI 🤖

</div>
