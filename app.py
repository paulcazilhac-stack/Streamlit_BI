import streamlit as st
import pandas as pd

st.set_page_config(page_title="Upload de Budget", layout="centered")

st.title("📊 Dépôt de Budget")

uploaded_file = st.file_uploader("Déposez votre fichier Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Fichier chargé avec succès.")
        st.write("Aperçu du budget :", df.head())

        # Sauvegarde locale
        df.to_excel("budget_utilisateur.xlsx", index=False)
        st.info("Fichier enregistré localement sous 'budget_utilisateur.xlsx'.")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")