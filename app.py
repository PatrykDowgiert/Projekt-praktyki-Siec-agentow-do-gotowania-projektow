import streamlit as st
from main import run_project_agent, save_files_to_disk

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="AgileDev Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (STYLIZACJA) ---
st.markdown("""
<style>
    /* Marginesy kontenera */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Wyśrodkowanie nagłówka */
    .header-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Karty agentów - Stylizacja */
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 auto;
    }
    
    .agent-card {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 10px;
        height: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        /* Wymuszenie czarnego tekstu dla czytelności */
        color: #000000 !important;
    }
    
    /* Kolory kart */
    .pm-card { background-color: #e3f2fd; border-left: 5px solid #2196f3; }
    .architect-card { background-color: #fff3e0; border-left: 5px solid #ff9800; }
    .coder-card { background-color: #e8f5e9; border-left: 5px solid #4caf50; }
    
    /* Teksty wewnątrz kart */
    .agent-card h4 { 
        margin-top: 0; 
        font-size: 1.1rem; 
        font-weight: bold;
        color: #000000 !important; 
    }
    .agent-card p { 
        font-size: 0.9rem; 
        margin-bottom: 0;
        color: #111111 !important; 
    }
    
    /* Wyśrodkowanie przycisku 'Poznaj Zespół' */
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
    }
    
    /* Ukrycie stopki Streamlit */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. NAGŁÓWEK ---
st.markdown("""
<div class="header-container">
    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" width="90" style="margin-bottom: 15px;">
    <h1 style="margin: 0; font-size: 2.5rem;">AgileDev Agents</h1>
    <p style="color: gray; font-size: 1.1rem; margin-top: 5px;">Twój autonomiczny zespół deweloperski AI</p>
</div>
""", unsafe_allow_html=True)

# --- 4. SEKCJA ZESPOŁU (ROZWIJANA) ---

if "show_team" not in st.session_state:
    st.session_state.show_team = False

def toggle_team():
    st.session_state.show_team = not st.session_state.show_team

# Przycisk
btn_label = "🔼 Ukryj Zespół" if st.session_state.show_team else "👥 Poznaj Zespół"
st.button(btn_label, on_click=toggle_team, type="secondary" if st.session_state.show_team else "primary")

# Warunkowe wyświetlanie kart
if st.session_state.show_team:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="agent-card pm-card">
            <h4>🕵️ Product Manager</h4>
            <p>Analizuje wymagania, tworzy backlog i pilnuje, by projekt miał sens biznesowy.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="agent-card architect-card">
            <h4>👷 Architekt Systemu</h4>
            <p>Planuje strukturę plików, dobiera technologie i zarządza zależnościami.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="agent-card coder-card">
            <h4>👨‍💻 Programista</h4>
            <p>Generuje czysty kod, dba o składnię i tworzy dokumentację techniczną.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()

# --- 5. INICJALIZACJA STANU ---

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Cześć! Jestem gotowy do pracy. Opisz projekt, a my zajmiemy się kodem."}
    ]

if "agent_state" not in st.session_state:
    st.session_state.agent_state = None 

if "project_name" not in st.session_state:
    st.session_state.project_name = "nowy_projekt"

# --- 6. SIDEBAR (PANEL BOCZNY) ---

with st.sidebar:
    st.header("📂 Zarządzanie")
    st.session_state.project_name = st.text_input("Nazwa projektu", value=st.session_state.project_name)
    
    st.markdown("---")
    
    if st.button("🧹 Resetuj Projekt", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_state = None
        st.rerun()
    
    # Podgląd plików
    if st.session_state.agent_state:
        files = st.session_state.agent_state.get("project_files", [])
        if files:
            st.divider()
            st.write(f"**Pliki w pamięci ({len(files)}):**")
            for f in files:
                with st.expander(f"📄 {f['name']}"):
                    st.code(f['content'], language='python')

# --- 7. OBSZAR CZATU ---

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 8. LOGIKA URUCHAMIANIA (Z PASKIEM POSTĘPU) ---

if prompt := st.chat_input("Opisz zadanie..."):
    # Dodaj wiadomość usera
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        
    with st.chat_message("assistant", avatar="🤖"):
        # Elementy UI do aktualizacji
        status_text = st.empty()
        progress_bar = st.progress(0, text="Inicjalizacja zespołu...")
        
        try:
            # Uruchamiamy silnik z main.py, przekazując pasek
            final_state = run_project_agent(
                prompt, 
                st.session_state.agent_state,
                progress_bar=progress_bar,
                status_text=status_text
            )
            
            # Zapisujemy stan
            st.session_state.agent_state = final_state
            
            # Zapisujemy pliki
            files = final_state.get("project_files", [])
            path = save_files_to_disk(st.session_state.project_name, files)
            
            # Czyścimy wskaźniki postępu
            progress_bar.empty()
            status_text.empty()
            
            # Budujemy odpowiedź końcową
            if files:
                response_text = f"✅ **Sukces!** Projekt zaktualizowany w folderze: `workspace/{st.session_state.project_name}`.\n\n**Lista plików:**\n"
                for f in files:
                    response_text += f"- `{f['name']}`\n"
            else:
                response_text = "Zakończono pracę. Nie wygenerowano nowych plików (czy to była tylko rozmowa?)."

            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            progress_bar.empty()
            st.error(f"Wystąpił błąd: {e}")
            status_text.error("Zatrzymano z powodu błędu.")