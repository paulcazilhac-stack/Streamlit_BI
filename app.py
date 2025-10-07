import streamlit as st
import pandas as pd
import os
from datetime import datetime
import shutil
import requests

# Configuration
st.set_page_config(page_title="Upload de Budget", layout="centered")
st.title("📊 Application Budget")

# Dossiers
budget_folder = r"C:\Users\PAUCAZ\PRIMEXIS\Contrôle de gestion - Documents\General\Conseil\2.-Offre Data\4. Automatisation\Plannification budgetaire auto\1. Données\BUDGET"
non_valide_folder = os.path.join(budget_folder, "Non validé")

# Webhook Teams
webhook_url = "https://primexis.webhook.office.com/webhookb2/ef9c5dfd-3d90-482a-9a57-3e6acf6c84ad@5c883d42-1d68-4ed8-ae00-b2ef5884358b/IncomingWebhook/845a30160177468792082b8e95e35fab/d968df2b-a6f3-4245-b0d6-3b1e7d7e4660/V27igqHYxZzvWS5GkJzgntnMmnb74l7MHniwATYPA7yXI1"

# Onglets
tab1, tab2 = st.tabs(["📥 Dépôt de Budget", "📁 Fichiers à valider"])

with tab1:
    uploaded_file = st.file_uploader("Déposez votre fichier Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            required_columns = {"Compte", "montant"}
            missing_columns = required_columns - set(df.columns)

            if missing_columns:
                st.error(f"Colonnes manquantes : {', '.join(missing_columns)}")
            else:
                st.success("Fichier chargé avec succès.")
                st.write("Aperçu du budget :", df.head())

                grouped_df = df.groupby("Compte", as_index=False)["montant"].sum()
                st.subheader("🧾 Synthèse par compte")
                st.dataframe(grouped_df)

                if st.button("✅ Valider l'import"):
                    timestamp = datetime.now().strftime("%Y%m%d%H%M")
                    filename = f"BUDGET{timestamp}BU.xlsx"
                    full_path = os.path.join(budget_folder, filename)

                    df["statut"] = "à valider"
                    df["Version"] = filename
                    df.to_excel(full_path, index=False)
                    st.success(f"Fichier enregistré sous : {full_path}")

        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

with tab2:
    st.subheader("📂 Fichiers en attente de validation")

    files = [f for f in os.listdir(budget_folder) if f.endswith(".xlsx") and f != "Non validé"]
    for file in files:
        file_path = os.path.join(budget_folder, file)
        try:
            df = pd.read_excel(file_path)
            statut = df["statut"].iloc[0] if "statut" in df.columns else "inconnu"
            version = df["Version"].iloc[0] if "Version" in df.columns else "non défini"

            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"📄 **{file}**")
                st.write(f"Statut : `{statut}`")
                st.write(f"Version : `{version}`")

            with col2:
                action = st.radio(f"Valider {file} ?", ["-", "Oui", "Non"], key=file)

            with col3:
                if st.button(f"🔄 Appliquer", key=f"apply_{file}"):
                    if action == "Oui":
                        df["statut"] = "en cours de validation"
                        df.to_excel(file_path, index=False)
                        st.success(f"{file} mis à jour avec statut 'en cours de validation'.")

                        # Envoi du message Teams
                        message = {
                            "text": f"✅ Le fichier **{file}** a été validé et est en cours de traitement."
                        }
                        response = requests.post(webhook_url, json=message)

                        if response.status_code == 200:
                            st.info("📨 Notification Teams envoyée à Paul.")
                        else:
                            st.error(f"Erreur lors de l'envoi du message Teams : {response.status_code}")

                    elif action == "Non":
                        df["statut"] = "non validé"
                        df.to_excel(file_path, index=False)

                        # Déplacement du fichier
                        if not os.path.exists(non_valide_folder):
                            os.makedirs(non_valide_folder)
                        shutil.move(file_path, os.path.join(non_valide_folder, file))
                        st.warning(f"{file} déplacé dans 'Non validé'.")
        except Exception as e:
            st.error(f"Erreur avec le fichier {file} : {e}")