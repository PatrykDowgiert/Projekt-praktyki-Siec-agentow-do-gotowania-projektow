import streamlit as st
import time
from main import generate_project, save_files

# Konfiguracja strony
st.set_page_config(page_title="Agile AI Dev Team", page_icon="🤖", layout="wide")

# Tytuł i opis
st.title("🤖 AgileDev Agents")
st.markdown("""
Twoja osobista sieć agentów AI. Opisz, co chcesz zbudować, a zespół:
1. **Product Manager** przeanalizuje wymagania.
2. **Architekt** zaprojektuje strukturę plików.
3. **Programista** napisze kod.
""")

# Sidebar z ustawieniami
with st.sidebar:
    st.header("⚙️ Ustawienia")
    project_name = st.text_input("Nazwa Projektu (folder)", value="moj_projekt")
    st.info("Projekt zostanie zapisany w folderze `workspace/`.")

# Główne pole tekstowe
user_prompt = st.text_area("Co budujemy dzisiaj?", height=150, placeholder="Np. Stwórz grę Snake w Pythonie...")

# Przycisk uruchamiający
if st.button("🚀 Uruchom Zespół", type="primary"):
    if not user_prompt:
        st.warning("Najpierw wpisz opis projektu!")
    else:
        # Kontener na statusy
        status_container = st.container()
        
        with st.status("Zespół pracuje...", expanded=True) as status:
            st.write("🕵️ **Product Manager** analizuje wymagania...")
            time.sleep(1) # Symulacja dla lepszego efektu UX
            
            st.write("👷 **Architekt** planuje strukturę plików...")
            time.sleep(1)
            
            st.write("👨‍💻 **Programista** pisze kod (to może chwilę potrwać)...")
            
            # --- TU DZIEJE SIĘ MAGIA ---
            generated_files = generate_project(user_prompt)
            # ---------------------------
            
            if isinstance(generated_files, dict) and "error" in generated_files:
                status.update(label="Błąd!", state="error")
                st.error(f"Wystąpił błąd: {generated_files['error']}")
            elif not generated_files:
                status.update(label="Coś poszło nie tak", state="error")
                st.error("Agenci nie zwrócili żadnych plików.")
            else:
                status.update(label="Gotowe! ✅", state="complete")
                
                # Zapis na dysk
                save_path = save_files(project_name, generated_files)
                st.success(f"Projekt zapisany w: `{save_path}`")
                
                # Wyświetlanie wyników
                st.subheader("📂 Wygenerowane pliki:")
                
                # Tworzymy zakładki dla każdego pliku
                file_names = [f['name'] for f in generated_files]
                tabs = st.tabs(file_names)
                
                for i, tab in enumerate(tabs):
                    with tab:
                        st.code(generated_files[i]['content'], language='python')