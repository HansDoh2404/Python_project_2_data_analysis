import streamlit as st
import pandas as pd
import seaborn as sns
from UI import *

st.set_page_config(page_title="Analyses Descriptives", page_icon="📈", layout="wide")  

if 'number_of_rows' not in st.session_state:
    st.session_state['number_of_rows'] = 10
    st.session_state['type'] = 'Categorical'

increment = st.sidebar.button('Etendre ➕')
if increment:
    st.session_state.number_of_rows += 1
decrement = st.sidebar.button('Réduire ➖')
if decrement:
    st.session_state.number_of_rows -= 1

df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

theme_plotly = None  # None or streamlit

# Style
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("##")

st.sidebar.header("Ajouter une nouvelle ligne")
options_form = st.sidebar.form("Options")
location = options_form.selectbox("Localisation", {"Urbain", "Rural"})
state = options_form.selectbox("Ville", {"Dodoma", "Kilimanjaro", "Dar es Salaam", "Kigoma", "Iringa", "Mwanza"})
region = options_form.selectbox("Région", {"Est", "Centre-Ouest", "Nord-Est", "Centre"})
investment = options_form.number_input("Somme investie")
construction = options_form.selectbox("Construction", {"Charpenterie", "Construction en métal", "Résistant au feu", "Maçonnerie"})
businesstype = options_form.selectbox("Type d'entreprise", {"Industrie", "Appartement", "Bâtiment de bureaux", "Ferme", "Construction", "Restaurant", "Hôtellerie", "Société / Firme", "Vente au détail", "Maçonnerie"})
earthquake = options_form.selectbox("Séisme", {"Oui", "Non"})
flood = options_form.selectbox("Inondation", {"Oui", "Non"})
rating = options_form.number_input("Rentabilité")
add_data = options_form.form_submit_button(label="Sauvegarder")

# Dictionary for ville to région mapping
ville_region = {
    "Dodoma": "Est",
    "Kigoma": "Centre-Ouest",
    "Iringa": "Centre-Ouest",
    "Dar es Salaam": "Est",
    "Mwanza": "Nord-Est",
    "Arusha": "Centre",
    "Kilimanjaro": "Nord-Est"
}

if add_data:
    if investment != 0 and location != "" and state in ville_region and ville_region[state] == region:
        new_data = pd.DataFrame.from_records([{
            'Localisation': location,
            'Ville': state,
            'Région': region,
            'Somme investie': int(investment),
            'Construction': construction,
            "Type d'entreprise": businesstype,
            'Séisme': earthquake,
            'Inondation': flood,
            'Rentabilité': float(rating)
        }])
        
        # Définir l'index du nouveau DataFrame pour qu'il commence à partir du dernier index de df + 1
        new_data.index = range(df.index[-1] + 1, df.index[-1] + 1 + len(new_data))

        # Concaténer les DataFrames
        df = pd.concat([df, new_data])
        try:
            df.to_excel("data.xlsx", index=False)
        except:
            st.warning("Fermer le dataset")
        st.success("Nouvelle ligne ajoutée avec succès !")
    else:
        st.sidebar.error("La ville et la région choisies ne correspondent pas.")
else:
    st.sidebar.error("Veuillez entrer une ligne valide")

# Afficher le DataFrame avec les colonnes sélectionnées
shwdata = st.multiselect('Filtre :', df.columns, default=["Localisation", "Ville", "Région", "Somme investie", "Construction", "Type d'entreprise", "Séisme", "Inondation"])

if shwdata:
    st.dataframe(df[shwdata].tail(st.session_state['number_of_rows']), use_container_width=True)
else:
    st.dataframe(df.tail(st.session_state['number_of_rows']), use_container_width=True)

st.sidebar.image("logo1.png", caption="")
