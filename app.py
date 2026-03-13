import streamlit as st
#from google import genai
from groq import Groq
import os
from dotenv import load_dotenv
import database as db

# 1. Inizializzazione Database
db.init_db()

# 2. Caricamento Variabili d'Ambiente (API Key)
load_dotenv()
#api_key = os.getenv("GEMINI_API_KEY")
api_key = os.getenv("GROQ_API_KEY")
st.set_page_config(page_title="Zingarate Planner", page_icon="🥷")

st.title("Top Secret Zingarate Planner 🥷")
st.write("Inserisci i tuoi desideri nell'ombra. Nessuno saprà cosa hai chiesto.")

# Stato della sessione per nascondere il form dopo l'invio
if "votato" not in st.session_state:
    st.session_state.votato = False

# --- SEZIONE INSERIMENTO (Invisibile dopo il voto) ---
if not st.session_state.votato:
    with st.form("preferenze_form"):
        budget = st.number_input("Budget massimo (€)", min_value=50, max_value=5000, value=400, step=50)
        periodo = st.text_input("Giorni/Periodo (es. Metà Agosto, 4 giorni)")
        must_have = st.text_area("Must Have (Cosa vuoi assolutamente?)", placeholder="Es. Mare, vita notturna, birra a fiumi...")
        deal_breaker = st.text_area("Deal Breaker (Cosa odi/non vuoi?)", placeholder="Es. Niente camminate, niente ostelli condivisi...")
        
        submitted = st.form_submit_button("Sigilla il mio voto segreto 🤐")
        
        if submitted:
            if periodo and must_have:
                db.insert_preferenza(budget, periodo, must_have, deal_breaker)
                st.session_state.votato = True
                st.rerun()
            else:
                st.error("Compila almeno il periodo e un 'Must Have'!")
else:
    st.success("✅ Il tuo voto è stato acquisito nel database segreto.")

st.divider()

# --- SEZIONE STATO E IA ---
df_preferenze = db.get_tutte_preferenze()
numero_votanti = len(df_preferenze)

st.subheader(f"📊 Voti segreti raccolti finora: {numero_votanti}")

# Mostra il bottone solo se c'è almeno un voto
if numero_votanti > 0:
    if st.button("🔮 Genera la Zingarata Definitiva", type="primary"):
        if not api_key or api_key == "inserisci_qui_la_tua_api_key_reale":
            st.error("⚠️ Manca la API Key di Gemini nel file .env!")
        else:
            # genai.configure(api_key=api_key)
            with st.spinner("L'IA sta mediando tra i vostri assurdi desideri..."):
                
                # Costruzione dinamica del prompt
                prompt = (
                    "Agisci come un tour operator esperto, spietato ma giusto. "
                    "Devi organizzare una vacanza di gruppo ('Zingarata'). "
                    "Ecco le richieste ANONIME dei partecipanti:\n\n"
                )
                
                for index, row in df_preferenze.iterrows():
                    prompt += f"Partecipante Anonimo {index+1}:\n"
                    prompt += f"- Budget max: {row['budget']}€\n"
                    prompt += f"- Periodo: {row['periodo']}\n"
                    prompt += f"- Vuole assolutamente: {row['must_have']}\n"
                    prompt += f"- Odia/Non tollera: {row['deal_breaker']}\n\n"
                    
                prompt += (
                    "Il tuo compito:\n"
                    "1. Trova una destinazione che NON violi i 'Deal Breaker' di nessuno.\n"
                    "2. Cerca di soddisfare i 'Must Have' e non superare il budget più basso indicato (o spiega il compromesso).\n"
                    "3. Proponi 2 o 3 opzioni diverse con stime di costo.\n"
                    "Usa un tono ironico ma fornisci informazioni utili e realistiche."
                )

                try:
                    # Inizializza il client Groq
                    client = Groq(api_key=api_key)
                    
                    # Chiamata al modello (usiamo LLaMA 3 70B, potentissimo e veloce)
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "Sei un tour operator esperto e ironico. Rispondi usando la formattazione Markdown."
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
    
    # ⚠️ CAMBIA QUESTA PASSWORD!
    if admin_pass == "Zingarata2026": 
        st.success("Accesso ai server sbloccato.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1. Salva i Dati")
            st.write("Scarica il database attuale sul tuo PC.")
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
            st.warning("⚠️ Caricare un file sovrascriverà i voti attuali!")
            uploaded_file = st.file_uploader("Carica il tuo file zingarate_backup.db", type=["db"])
            
            if uploaded_file is not None:
                if st.button("🔥 Conferma Ripristino"):
                    # Sovrascrive il file del server con quello caricato
                    with open("zingarate.db", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success("Database ripristinato! Ricarico l'app...")
                    st.rerun()
                    
    elif admin_pass != "":
        st.error("⛔ Password errata. Fuori di qui.")
                