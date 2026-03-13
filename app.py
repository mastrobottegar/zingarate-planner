import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import database as db

# 1. Inizializzazione Database
db.init_db()

# 2. Caricamento Variabili d'Ambiente (API Key)
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
st.set_page_config(page_title="Zingarate Planner", page_icon="🥷")

st.title("Top Secret Zingarate Planner 🥷")
st.write("Inserisci i tuoi desideri nell'ombra. Nessuno saprà cosa hai chiesto.")

# Stato della sessione per nascondere il form dopo l'invio
if "votato" not in st.session_state:
    st.session_state.votato = False

# --- SEZIONE INSERIMENTO (Invisibile dopo il voto) ---
if not st.session_state.votato:
    st.subheader("💡 Configura la tua Zingarata")
    
    with st.form(key="preferenze_form", clear_on_submit=True):
        
        # --- 1. IDENTITÀ E BUDGET ---
        st.markdown("#### 👤 Chi sei e quanto sganci?")
        col_i1, col_i2 = st.columns(2)
        with col_i1:
            autore = st.text_input("Il tuo nome", placeholder="Es. Marco")
        with col_i2:
            budget = st.number_input("Budget massimo (€)", min_value=50, max_value=5000, value=400, step=50)
        
        st.divider()
        
        # --- 2. IL REBUS DELLE DATE ---
        st.markdown("#### 📅 Le Date")
        st.write("Inserisci giorni esatti (es. 12-15 nov) o periodi (es. weekend di ottobre).")
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            date_preferite = st.text_input("🟢 Date Preferite")
        with col_d2:
            date_evitare = st.text_input("🟡 Date da Evitare")
        with col_d3:
            date_impossibili = st.text_input("🔴 Date Impossibili")

        st.divider()

        # --- 3. I GUSTI PERSONALI ---
        st.markdown("#### 🎯 Cosa vogliamo fare?")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            amerei_fare = st.text_area("😍 Cosa AMEREI fare", placeholder="Es. Tour enogastronomico, terme...", height=100)
            preferisco_fare = st.text_area("🙂 Cosa PREFERISCO fare", placeholder="Es. Girare in centro a piedi...", height=100)
        with col_g2:
            voglio_evitare = st.text_area("🥱 Cosa VOGLIO EVITARE", placeholder="Es. Alzatacce alle 6, troppi musei...", height=100)
            assolutamente_no = st.text_area("🚫 Assolutamente NO", placeholder="Es. Ostelli condivisi, discoteche...", height=100)

        st.divider()

        # --- 4. L'IDEA DI BASE ---
        st.markdown("#### 🌍 La tua Proposta (Opzionale)")
        proposta_testuale = st.text_area(
            "Hai già in mente una destinazione o un'idea specifica? Scrivila qui:",
            placeholder="Es: Raga andiamo a Monaco a bere birra, oppure a Lisbona...",
            height=100
        )
        
        submitted = st.form_submit_button("Sigilla il mio voto segreto 🤐", type="primary")
        
        if submitted:
            if not autore:
                st.error("⚠️ Inserisci almeno il tuo nome per votare!")
            else:
                # Inserimento nel DB aggiornato
                db.insert_preferenza(
                    autore, budget, date_preferite, date_evitare, date_impossibili,
                    amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale
                )
                st.session_state.votato = True
                st.rerun()
else:
    st.success("✅ Il tuo profilo di viaggio è stato acquisito nel database segreto.")

st.divider()

# --- SEZIONE STATO E IA ---
df_preferenze = db.get_tutte_preferenze()
numero_votanti = len(df_preferenze)

st.subheader(f"📊 Voti segreti raccolti finora: {numero_votanti}")

# Mostra il bottone solo se c'è almeno un voto
if numero_votanti > 0:
    if st.button("🔮 Genera la Zingarata Definitiva", type="primary"):
        if not api_key or api_key == "inserisci_qui_la_tua_api_key_reale":
            st.error("⚠️ Manca la API Key di Groq nel file Secrets!")
        else:
            with st.spinner("L'IA sta decifrando le vostre complesse esigenze..."):
                
                # Costruzione dinamica del prompt con i nuovi campi
                prompt = (
                    "Agisci come un tour operator esperto, spietato ma giusto. "
                    "Devi organizzare una vacanza di gruppo ('Zingarata'). "
                    "Ecco le richieste dettagliate dei partecipanti:\n\n"
                )
                
                for index, row in df_preferenze.iterrows():
                    prompt += f"👤 PARTECIPANTE: {row.get('autore', f'Anonimo {index+1}')}\n"
                    prompt += f"- Budget max: {row.get('budget', 'N/D')}€\n"
                    prompt += f"- Date Preferite: {row.get('date_preferite', 'N/D')}\n"
                    prompt += f"- Date da Evitare: {row.get('date_evitare', 'N/D')}\n"
                    prompt += f"- Date Impossibili: {row.get('date_impossibili', 'N/D')}\n"
                    prompt += f"- Amerebbe fare: {row.get('amerei_fare', 'N/D')}\n"
                    prompt += f"- Preferisce fare: {row.get('preferisco_fare', 'N/D')}\n"
                    prompt += f"- Vuole evitare: {row.get('voglio_evitare', 'N/D')}\n"
                    prompt += f"- Assolutamente NO: {row.get('assolutamente_no', 'N/D')}\n"
                    prompt += f"- Proposta specifica: {row.get('proposta_testuale', 'Nessuna')}\n\n"
                    
                prompt += (
                    "Il tuo compito:\n"
                    "1. Analizza le date di tutti e trova il periodo migliore in cui NESSUNO ha 'Date Impossibili'.\n"
                    "2. Trova una destinazione che rispetti rigorosamente i 'Assolutamente NO' di tutti.\n"
                    "3. Cerca di soddisfare i 'Amerebbe fare' e non superare il budget più basso indicato dal gruppo.\n"
                    "4. Valuta le 'Proposte specifiche' scritte dai partecipanti: se una è fattibile per tutti, promuovila.\n"
                    "5. Proponi 2 o 3 opzioni di viaggio (Destinazione + Date stimate + Costo stimato + Motivazione).\n"
                    "Usa un tono ironico, bacchetta chi ha fatto richieste assurde, ma fornisci informazioni utili e realistiche. Formatta la risposta in Markdown pulito."
                )

                try:
                    client = Groq(api_key=api_key)
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "Sei un tour operator esperto e ironico. Organizzi viaggi per gruppi di amici molto complicati."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.7,
                    )
                    
                    st.subheader("🗺️ La Sentenza dell'IA (Powered by Groq)")
                    st.markdown(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Si è verificato un errore con l'IA: {e}")

st.divider()

# --- AREA ADMIN (Nascosta) ---
with st.expander("🛠️ Area Admin Segreta"):
    st.write("Solo per il Tour Operator. Inserisci la password per gestire il database.")
    admin_pass = st.text_input("Password di sblocco", type="password")
    
    if admin_pass == "Zingarata2026": 
        st.success("Accesso ai server sbloccato.")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1. Salva i Dati")
            try:
                with open("zingarate.db", "rb") as f:
                    db_bytes = f.read()
                st.download_button(
                    label="💾 Scarica Backup (.db)",
                    data=db_bytes,
                    file_name="zingarate_backup.db",
                    mime="application/octet-stream",
                    type="primary"
                )
            except FileNotFoundError:
                st.error("Nessun database trovato.")
                
        with col2:
            st.subheader("2. Ripristina Dati")
            uploaded_file = st.file_uploader("Carica zingarate_backup.db", type=["db"])
            if uploaded_file is not None:
                if st.button("🔥 Conferma Ripristino"):
                    with open("zingarate.db", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success("Database ripristinato! Ricarico l'app...")
                    st.rerun()
                    
    elif admin_pass != "":
        st.error("⛔ Password errata. Fuori di qui.")
