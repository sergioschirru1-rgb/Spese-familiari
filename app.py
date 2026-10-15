import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Gestione Spese Famigliari", page_icon="💰", layout="wide"
)

DATA_FILE = "spese.csv"

# Inizializzazione dati con salvataggio su file CSV per non perderli
if "df_spese" not in st.session_state:
  try:
    st.session_state.df_spese = pd.read_csv(DATA_FILE)
  except FileNotFoundError:
    st.session_state.df_spese = pd.DataFrame(
        columns=["Data", "Categoria", "Chi", "Importo", "Descrizione"]
    )

st.title("💰 Gestione Spese Famigliari Avanzata")

# --- BARRA LATERALE: BUDGET E FILTRI ---
st.sidebar.header("⚙️ Impostazioni & Budget")
budget_mensile = st.sidebar.number_input(
    "Budget Mensile (€)", min_value=0.0, value=1000.0, step=50.0
)

# --- SEZIONE INSERIMENTO SPESA ---
st.subheader("➕ Aggiungi una Spesa")
with st.form("form_spesa", clear_on_submit=True):
  col1, col2, col3 = st.columns(3)
  with col1:
    data_spesa = st.date_input("Data", datetime.date.today())
  with col2:
    categoria = st.selectbox(
        "Categoria",
        [
            "Spesa/Alimentari",
            "Bollette/Utenze",
            "Casa/Affitto/Mutuo",
            "Trasporti/Auto",
            "Svago/Tempo Libero",
            "Salute",
            "Altro",
        ],
    )
  with col3:
    chi = st.selectbox("Chi ha speso?", ["Sergio", "Altro componente", "Famiglia"])

  col4, col5 = st.columns(2)
  with col4:
    importo = st.number_input("Importo (€)", min_value=0.01, value=10.0, step=1.0)
  with col5:
    descrizione = st.text_input("Descrizione (opzionale)")

  submitted = st.form_submit_button("Salva Spesa")
  if submitted:
    nuova_riga = pd.DataFrame({
        "Data": [str(data_spesa)],
        "Categoria": [categoria],
        "Chi": [chi],
        "Importo": [importo],
        "Descrizione": [descrizione],
    })
    st.session_state.df_spese = pd.concat(
        [st.session_state.df_spese, nuova_riga], ignore_index=True
    )
    st.session_state.df_spese.to_csv(DATA_FILE, index=False)
    st.success("Spesa salvata con successo!")
    st.rerun()

df = st.session_state.df_spese

if not df.empty:
  df["Data"] = pd.to_datetime(df["Data"])
  df["Mese"] = df["Data"].dt.to_period("M").astype(str)

  # --- FILTRI NELLA SIDEBAR ---
  st.sidebar.markdown("---")
  st.sidebar.header("🔍 Filtri")
  mesi_disponibili = sorted(df["Mese"].unique(), reverse=True)
  mese_selezionato = st.sidebar.selectbox(
      "Filtra per Mese", ["Tutti"] + list(mesi_disponibili)
  )

  persone_disponibili = sorted(df["Chi"].unique())
  persona_selezionata = st.sidebar.selectbox(
      "Filtra per Persona", ["Tutti"] + list(persone_disponibili)
  )

  # Applicazione filtri
  df_filtrato = df.copy()
  if mese_selezionato != "Tutti":
    df_filtrato = df_filtrato[df_filtrato["Mese"] == mese_selezionato]
  if persona_selezionata != "Tutti":
    df_filtrato = df_filtrato[df_filtrato["Chi"] == persona_selezionata]

  # --- BUDGET E BARRA DI AVANZAMENTO ---
  mese_corrente = datetime.date.today().strftime("%Y-%m")
  totale_speso_mese = (
      df[df["Mese"] == mese_corrente]["Importo"].sum() if not df.empty else 0
  )

  st.markdown("---")
  col_m1, col_m2 = st.columns(2)
  with col_m1:
    st.metric(
        label=f"Speso nel mese corrente ({mese_corrente})",
        value=f"€ {totale_speso_mese:.2f}",
    )
  with col_m2:
    percentuale = (
        min(totale_speso_mese / budget_mensile, 1.0)
        if budget_mensile > 0
        else 0
    )
    st.metric(
        label="Budget Mensile",
        value=f"€ {budget_mensile:.2f}",
        delta=f"Restante: € {budget_mensile - totale_speso_mese:.2f}",
    )

  st.progress(
      percentuale,
      text=f"Utilizzato il {percentuale*100:.1f}% del budget stabilito",
  )
  st.markdown("---")

  # --- TABELLA E CANCELLAZIONE ---
  st.subheader("📋 Elenco Spese Registrate")
  col_tab, col_del = st.columns([3, 1])

  with col_tab:
    st.dataframe(
        df_filtrato.sort_values(by="Data", ascending=False),
        use_container_width=True,
    )

  with col_del:
    st.write("### Elimina spesa")
    indice_da_eliminare = st.number_input(
        "N. riga da eliminare",
        min_value=0,
        max_value=max(0, len(df) - 1),
        step=1,
    )
    if st.button("Elimina"):
      df = df.drop(index=indice_da_eliminare).reset_index(drop=True)
      st.session_state.df_spese = df
      st.session_state.df_spese.to_csv(DATA_FILE, index=False)
      st.success("Spesa eliminata!")
      st.rerun()

  # --- ESPORTAZIONE DATI ---
  st.download_button(
      label="📥 Scarica tutte le spese (CSV)",
      data=df.to_csv(index=False).encode("utf-8"),
      file_name="spese_famigliari.csv",
      mime="text/csv",
  )

  st.markdown("---")

  # --- GRAFICI E STATISTICHE ---
  st.subheader("📊 Statistiche e Grafici")
  c1, c2 = st.columns(2)

  with c1:
    st.markdown("**Spese per Categoria**")
    if not df_filtrato.empty:
      st.bar_chart(df_filtrato.groupby("Categoria")["Importo"].sum())
    else:
      st.info("Nessun dato disponibile.")

  with c2:
    st.markdown("**Spese per Componente**")
    if not df_filtrato.empty:
      st.bar_chart(df_filtrato.groupby("Chi")["Importo"].sum())
    else:
      st.info("Nessun dato disponibile.")

else:
  st.info("Nessuna spesa registrata al momento. Inizia ad aggiungerne una sopra!")

