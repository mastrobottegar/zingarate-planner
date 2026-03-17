import streamlit as st
import requests
import os
import random
from dotenv import load_dotenv
import database as db

# 1. Inizializzazione Database
db.init_db()

# 2. Caricamento Variabili d'Ambiente
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
st.set_page_config(page_title="Zingarate Planner", page_icon="🥷")

st.title("Top Secret Zingarate Planner 🥷")
st.write("Inserisci i tuoi desideri nell'ombra. Nessuno saprà cosa hai chiesto.")

# --- GESTIONE STATO DI SESSIONE ---
if "utente_corrente" not in st.session_state:
    st.session_state.utente_corrente = None
if "dati_utente" not in st.session_state:
    st.session_state.dati_utente = None
if "votato" not in st.session_state:
    st.session_state.votato = False

# --- STEP 1: IDENTIFICAZIONE (Login Invisibile) ---
if st.session_state.utente_corrente is None:
    st.subheader("👤 Identificazione")
    nome_input = st.text_input("Inserisci il tuo nome per votare o modificare le tue preferenze:")
    
    if st.button("Entra 🚪", type="primary"):
        if nome_input:
            # Pulizia automatica del nome (rimuove spazi e mette la prima maiuscola)
            nome_pulito = nome_input.strip().title()
            
            # Cerca nel DB se l'utente esiste già
            dati_esistenti = db.get_preferenza_autore(nome_pulito)
            
            st.session_state.utente_corrente = nome_pulito
            if dati_esistenti:
                st.session_state.dati_utente = dati_esistenti
                st.success(f"Bentornato {nome_pulito}! Ho recuperato le tue vecchie preferenze.")
            else:
                st.session_state.dati_utente = {}
                st.info(f"Benvenuto {nome_pulito}! Sei un nuovo partecipante.")
            st.rerun()
        else:
            st.warning("Devi inserire un nome per procedere!")

# --- STEP 2: IL FORM (Visibile solo dopo aver inserito il nome) ---
elif not st.session_state.votato:
    st.subheader(f"💡 Configura la tua Zingarata, {st.session_state.utente_corrente}")
    st.write("Se modifichi i dati e salvi, le tue vecchie preferenze verranno sovrascritte.")
    
    # Recuperiamo i dati vecchi se esistono (altrimenti stringhe vuote o default)
    du = st.session_state.dati_utente
    
    with st.form(key="preferenze_form", clear_on_submit=False):
        
        # --- 1. IDENTITÀ E BUDGET ---
        st.markdown("#### 💰 Il Budget")
        budget = st.number_input("Budget massimo (€)", min_value=50, max_value=5000, value=int(float(du.get("budget") or 400)), step=50)        
        st.divider()
        
        # --- 2. IL REBUS DELLE DATE ---
        st.markdown("#### 📅 Le Date")
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            date_preferite = st.text_input("🟢 Date Preferite", value=du.get("date_preferite", ""))
        with col_d2:
            date_evitare = st.text_input("🟡 Date da Evitare", value=du.get("date_evitare", ""))
        with col_d3:
            date_impossibili = st.text_input("🔴 Date Impossibili", value=du.get("date_impossibili", ""))

        st.divider()

        # --- 3. I GUSTI PERSONALI ---
        st.markdown("#### 🎯 Cosa vogliamo fare?")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            amerei_fare = st.text_area("😍 Cosa AMEREI fare", value=du.get("amerei_fare", ""), height=100)
            preferisco_fare = st.text_area("🙂 Cosa PREFERISCO fare", value=du.get("preferisco_fare", ""), height=100)
        with col_g2:
            voglio_evitare = st.text_area("🥱 Cosa VOGLIO EVITARE", value=du.get("voglio_evitare", ""), height=100)
            assolutamente_no = st.text_area("🚫 Assolutamente NO", value=du.get("assolutamente_no", ""), height=100)

        st.divider()

        # --- 4. L'IDEA DI BASE ---
        st.markdown("#### 🌍 La tua Proposta (Opzionale)")
        proposta_testuale = st.text_area(
            "Hai in mente una destinazione specifica?",
            value=du.get("proposta_testuale", ""),
            height=100
        )
        
        submitted = st.form_submit_button("Sigilla le mie preferenze 🤐", type="primary")
        
        if submitted:
            # Inserimento o Aggiornamento nel DB
            db.upsert_preferenza(
                st.session_state.utente_corrente, budget, date_preferite, date_evitare, date_impossibili,
                amerei_fare, preferisco_fare, voglio_evitare, assolutamente_no, proposta_testuale
            )
            st.session_state.votato = True
            st.rerun()

    # Bottone per cambiare utente se si è sbagliato a digitare
    if st.button("Esci / Cambia Utente"):
        st.session_state.utente_corrente = None
        st.session_state.dati_utente = None
        st.rerun()

else:
    st.success(f"✅ Ottimo lavoro, {st.session_state.utente_corrente}. Il tuo profilo è blindato nel database.")
    if st.button("Modifica le mie preferenze"):
        st.session_state.votato = False
        st.rerun()

st.divider()

# --- SEZIONE STATO E IA ---
df_preferenze = db.get_tutte_preferenze()
numero_votanti = len(df_preferenze)

st.subheader(f"📊 Voti segreti raccolti finora: {numero_votanti}")

if numero_votanti > 0:
    if st.button("🔮 Genera la Zingarata Definitiva", type="primary"):
        # Ora peschiamo la chiave di Mistral
        # Il sistema infallibile per pescare la chiave
        if "MISTRAL_API_KEY" in st.secrets:
            api_key = st.secrets["MISTRAL_API_KEY"] # Cerca su Streamlit Cloud
        else:
            api_key = os.getenv("MISTRAL_API_KEY")  # Cerca sul tuo PC locale (.env) 
        if not api_key:
            st.error("⚠️ Manca la API Key di Mistral nei Secrets!")
        else:
            with st.spinner("Connessione ai server europei di Mistral in corso..."):
                
                # 1. SHUFFLE: Mescoliamo l'ordine delle righe a caso
                df_mescolato = df_preferenze.sample(frac=1).reset_index(drop=True)
                
                # 2. GENERAZIONE NOMI IN CODICE
                nomi_base = ["Falco", "Cobra", "Volpe", "Lupo", "Orso", "Tigre", "Vipera", "Corvo", "Squalo", "Pantera", "Grizzly", "Mamba"]
                nomi_in_codice = random.sample(nomi_base, min(numero_votanti, len(nomi_base)))
                
                # 3. COSTRUZIONE DEL PROMPT ANONIMO
                prompt = (
                    "Ecco le richieste dettagliate e ANONIME dei partecipanti. "
                    "Usa ESCLUSIVAMENTE i loro Nomi in Codice per riferirti a loro.\n\n"
                )
                
                for index, row in df_mescolato.iterrows():
                    agente = f"Agente {nomi_in_codice[index]}"
                    prompt += f"👤 {agente}:\n"
                    prompt += f"- Budget max: {row.get('budget', 'N/D')}€\n"
                    prompt += f"- Date Preferite: {row.get('date_preferite', 'N/D')}\n"
                    prompt += f"- Date da Evitare: {row.get('date_evitare', 'N/D')}\n"
                    prompt += f"- Date Impossibili: {row.get('date_impossibili', 'N/D')}\n"
                    prompt += f"- Amerebbe fare: {row.get('amerei_fare', 'N/D')}\n"
                    prompt += f"- Vuole evitare: {row.get('voglio_evitare', 'N/D')}\n"
                    prompt += f"- Assolutamente NO (Veto assoluto): {row.get('assolutamente_no', 'N/D')}\n"
                    
                    if row.get('proposta_testuale'):
                        prompt += f"- Proposta specifica: {row.get('proposta_testuale')}\n\n"
                    else:
                        prompt += "\n"
                    
                prompt += (
                    "IL TUO COMPITO (Valutazione e Piano Operativo):\n"
                    "Fase 1: Il Pagellone delle Proposte\n"
                    "Per ogni proposta emersa (se non ce ne sono, proponine tu un paio realistiche basandoti sui gusti incrociati):\n"
                    "- Assegna uno 'Zinga-Score' (da 1 a 10).\n"
                    "- Elenca i MATCH 🟢 (chi è felice e perché).\n"
                    "- Elenca i MISMATCH 🔴 (quali veti vengono violati e da chi).\n"
                    "- Sii ironico e severo con chi ha fatto richieste fuori dal mondo o con budget irrealistici.\n\n"
                    "Fase 2: Il Dossier Operativo (La Meta Vincitrice)\n"
                    "- Decreta la meta VINCITRICE assoluta (quella che fa meno danni al gruppo e sopravvive ai veti).\n"
                    "- Stila un Programma Dettagliato Day-by-Day (Giorno 1, Giorno 2...) diviso in Mattina, Pomeriggio e Sera per la meta vincitrice.\n"
                    "- Specifica nel programma COME le singole attività incastrano i paletti degli agenti.\n\n"
                    "Formatta tutto in Markdown pulito."
                )

                try:
                    # Chiamata DIRETTA e infallibile al server
                    url = "https://api.mistral.ai/v1/chat/completions"
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }
                    payload = {
                        "model": "open-mistral-nemo",
                        "temperature": 0.7,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Sei un tour operator esperto, inflessibile e ironico. Sei il Direttore delle Operazioni per le vacanze di gruppo."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                    
                    risposta = requests.post(url, headers=headers, json=payload)
                    
                    if risposta.status_code == 200:
                        testo_ia = risposta.json()["choices"][0]["message"]["content"]
                        st.subheader("🗺️ Il Dossier della Missione (Classificato)")
                        st.markdown(testo_ia)
                    else:
                        st.error(f"Il server Mistral ha respinto la richiesta. Codice: {risposta.status_code} - Dettagli: {risposta.text}")
                        
                except Exception as e:
                    st.error(f"Errore di rete: {e}")

st.divider()

# --- AREA ADMIN (Nascosta) ---
with st.expander("🛠️ Area Admin Segreta"):
    st.write("Solo per il Tour Operator. Inserisci la password per gestire il database.")
    admin_pass = st.text_input("Password di sblocco", type="password")
    
    if admin_pass == "Zingarata2026": 
        st.success("Accesso ai server sbloccato.")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("1. Salva i Dati")
            try:
                with open("zingarate.db", "rb") as f:
                    db_bytes = f.read()
                st.download_button(
                    label="💾 Scarica Backup",
                    data=db_bytes,
                    file_name="zingarate_backup.db",
                    mime="application/octet-stream",
                    type="primary"
                )
            except FileNotFoundError:
                st.error("Nessun db trovato.")
                
        with col2:
            st.subheader("2. Ripristina")
            uploaded_file = st.file_uploader("Carica backup", type=["db"])
            if uploaded_file is not None:
                if st.button("🔥 Conferma"):
                    with open("zingarate.db", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success("Ripristinato!")
                    st.rerun()
                    
        with col3:
            st.subheader("3. Protocollo Ghost")
            st.warning("⚠️ Cancella TUTTO")
            if st.button("🚨 Svuota DB"):
                db.svuota_db()
                # Resettiamo anche la memoria locale della tua sessione
                st.session_state.votato = False
                st.session_state.utente_corrente = None
                st.session_state.dati_utente = None
                st.success("Boom! Database piallato. Ricarico...")
                st.rerun()
                    
    elif admin_pass != "":
        st.error("⛔ Password errata. Fuori di qui.")
