import streamlit as st
from main import run_project_agent, save_files_to_disk

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="AgileDev Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS (STYLIZACJA) ---
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .header-container {
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* Karty agentów */
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 auto;
    }
    
    .agent-card {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 10px;
        height: 100%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        /* WYMUSZENIE CZARNEGO TEKSTU: */
        color: #000000 !important;
    }
    
    .pm-card { background-color: #e3f2fd; border-left: 5px solid #2196f3; }
    .architect-card { background-color: #fff3e0; border-left: 5px solid #ff9800; }
    .coder-card { background-color: #e8f5e9; border-left: 5px solid #4caf50; }
    
    /* Wymuszenie koloru dla nagłówków i paragrafów wewnątrz kart */
    .agent-card h4 { 
        margin-top: 0; 
        font-size: 1.0rem; 
        font-weight: bold;
        color: #000000 !important; 
    }
    .agent-card p { 
        font-size: 0.85rem; 
        margin-bottom: 0;
        color: #222222 !important; /* Bardzo ciemny szary dla czytelności */
    }
    
    /* Wyśrodkowanie przycisku */
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# --- NAGŁÓWEK ---
st.markdown("""
<div class="header-container">
    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" width="80" style="margin-bottom: 10px;">
    <h1 style="margin: 0; font-size: 2.2rem;">AgileDev Agents</h1>
    <p style="color: gray; margin-top: 5px;">Twój autonomiczny zespół deweloperski AI</p>
</div>
""", unsafe_allow_html=True)

# --- PRZYCISK POKAŻ/UKRYJ ZESPÓŁ ---

if "show_team" not in st.session_state:
    st.session_state.show_team = False

def toggle_team():
    st.session_state.show_team = not st.session_state.show_team

label = "🔼 Ukryj Zespół" if st.session_state.show_team else "👥 Poznaj Zespół"
st.button(label, on_click=toggle_team, type="secondary" if st.session_state.show_team else "primary")

# --- WARUNKOWE WYŚWIETLANIE ZESPOŁU ---
if st.session_state.show_team:
    with st.container():
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("""
            <div class="agent-card pm-card">
                <h4>🕵️ Product Manager</h4>
                <p>Tworzy backlog i pilnuje wymagań biznesowych.</p>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="agent-card architect-card">
                <h4>👷 Architekt Systemu</h4>
                <p>Planuje strukturę plików i dobiera technologie.</p>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown("""
            <div class="agent-card coder-card">
                <h4>👨‍💻 Programista</h4>
                <p>Generuje czysty kod Python plik po pliku.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

# --- LOGIKA APLIKACJI (CHAT) ---

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Cześć! Jestem gotowy do pracy. Co budujemy?"}
    ]

if "agent_state" not in st.session_state:
    st.session_state.agent_state = None 

if "project_name" not in st.session_state:
    st.session_state.project_name = "nowy_projekt"

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 Zarządzanie")
    st.session_state.project_name = st.text_input("Nazwa projektu", value=st.session_state.project_name)
    
    if st.button("🧹 Resetuj Projekt", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_state = None
        st.rerun()
    
    if st.session_state.agent_state:
        files = st.session_state.agent_state.get("project_files", [])
        if files:
            st.divider()
            st.caption(f"Pliki w pamięci: {len(files)}")
            for f in files:
                with st.expander(f"📄 {f['name']}"):
                    st.code(f['content'], language='python')

# --- CHAT AREA ---
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Opisz zadanie..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        
    with st.chat_message("assistant", avatar="🤖"):
        status_container = st.empty()
        with st.status("🚀 Agenci pracują...", expanded=True) as status:
            try:
                final_state = run_project_agent(prompt, st.session_state.agent_state)
                st.session_state.agent_state = final_state
                
                files = final_state.get("project_files", [])
                path = save_files_to_disk(st.session_state.project_name, files)
                
                status.update(label="Gotowe! ✅", state="complete", expanded=False)
                
                if files:
                    response_text = f"Zaktualizowano projekt w folderze: `workspace/{st.session_state.project_name}`.\n\n**Pliki:**\n" + "\n".join([f"- `{f['name']}`" for f in files])
                else:
                    response_text = "Zakończono pracę (brak nowych plików)."

                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"Błąd: {e}")
                status.update(label="Błąd", state="error")