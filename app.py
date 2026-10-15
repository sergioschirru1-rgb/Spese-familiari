import streamlit as st
import pandas as pd
import datetime
import os

# Titolo e configurazione pagina
st.set_page_config(page_title="Gestione Spese Familiari", page_icon="💰", layout="centered")
st.title("💰 Gestione Spese Familiari")

FILE_DATI = "spese_famiglia.csv"

# Inizializzazione o caricamento dati
def carica_dati():
    if os.path.exists(FILE_DATI):
        return pd.read_csv(FILE_DATI)
    else:
        return pd.DataFrame(columns=["Data", "Membro", "Categoria", "Descrizione", "Importo (€)"])

df = carica_dati()

# --- SEZIONE 1: NUOVA SPESA ---
st.subheader("➕ Aggiungi una Spesa")

with st.form("form_spesa", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.date.today())
        membro = st.selectbox("Chi ha speso?", ["Papà", "Mamma", "Figlio/a", "Altro"])
    with col2:
        categoria = st.selectbox("Categoria", ["Spesa/Alimentari", "Bollette/Casa", "Trasporti/Auto", "Svago/Ristoranti", "Salute", "Altro"])
        importo = st.number_input("Importo (€)", min_value=0.01, step=0.50, format="%.2f")
    
    descrizione = st.text_input("Descrizione (opzionale)")
    invia = st.form_submit_button("Salva Spesa")

if invia:
    nuova_spesa = pd.DataFrame([{
        "Data": str(data),
        "Membro": membro,
        "Categoria": categoria,
        "Descrizione": descrizione,
        "Importo (€)": importo
    }])
    df = pd.concat([df, nuova_spesa], ignore_index=True)
    df.to_csv(FILE_DATI, index=False)
    st.success("Spesa salvata con successo!")
    st.rerun()

# --- SEZIONE 2: RIEPILOGO E GRAFICI ---
if not df.empty:
    st.markdown("---")
    st.subheader("📊 Totali e Statistiche")
    
    # Conversione data
    df["Data"] = pd.to_datetime(df["Data"])
    
    # Metriche principali
    totale_generale = df["Importo (€)"].sum()
    st.metric("Totale Speso Complessivo", f"{totale_generale:.2f} €")
    
    # Grafico per categoria
    spese_per_cat = df.groupby("Categoria")["Importo (€)"].sum()
    st.bar_chart(spese_per_cat)

    # --- SEZIONE 3: REGISTRO SPESE ---
    st.markdown("---")
    st.subheader("📜 Storico Spese")
    st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)
else:
    st.info("Nessuna spesa registrata al momento.")
