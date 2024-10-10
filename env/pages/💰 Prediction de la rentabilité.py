import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import itertools

# Set Streamlit configuration
st.set_page_config(page_title="Analyses Descriptives", page_icon="📈", layout="wide")

# Load data
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

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

# Update dataframe with région information based on ville
df["Région"] = df["Ville"].map(ville_region)

# Prepare the data
X = df.drop(columns=["Rentabilité"])
y = df["Rentabilité"]

# Convert categorical variables to numerical using one-hot encoding
X = pd.get_dummies(X, drop_first=True)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Function to predict profitability based on user input
def predict_profitability(location, city, investment, construction, businesstype, earthquake, flood):
    # Map city to region
    region = ville_region.get(city, "")

    # Check if investment is zero
    if investment == 0:
        return "Erreur : La somme investie ne peut pas être zéro."

    # Prepare input data for prediction
    input_data = {
        'Localisation': [location],
        'Ville': [city],
        'Région': [region],
        'Somme investie': [investment],
        'Construction': [construction],
        'Type d\'entreprise': [businesstype],
        'Séisme': [1 if earthquake == "Oui" else 0],
        'Inondation': [1 if flood == "Oui" else 0]
    }

    # Create DataFrame from input data
    input_df = pd.DataFrame(input_data)

    # Convert categorical variables to numerical
    input_df = pd.get_dummies(input_df, drop_first=True)

    # Ensure input DataFrame has the same columns as X
    input_df = input_df.reindex(columns=X.columns, fill_value=0)

    # Predict profitability
    predicted_profitability = model.predict(input_df)[0]

    return predicted_profitability

# Find combinations that yield max and min rentability
unique_values = {
    'Localisation': df['Localisation'].unique(),
    'Ville': df['Ville'].unique(),
    'Région': df['Région'].unique(),
    'Somme investie': [df['Somme investie'].min(), df['Somme investie'].max()],
    'Construction': df['Construction'].unique(),
    'Type d\'entreprise': df['Type d\'entreprise'].unique(),
    'Séisme': [0, 1],
    'Inondation': [0, 1]
}

combinations = list(itertools.product(*unique_values.values()))
combinations_df = pd.DataFrame(combinations, columns=unique_values.keys())

# Convert categorical variables to numerical
combinations_df = pd.get_dummies(combinations_df, drop_first=True)
combinations_df = combinations_df.reindex(columns=X.columns, fill_value=0)

predictions = model.predict(combinations_df)
max_index = np.argmax(predictions)
min_index = np.argmin(predictions)

max_combination = dict(zip(unique_values.keys(), combinations[max_index]))
min_combination = dict(zip(unique_values.keys(), combinations[min_index]))

# Sidebar for user input
st.sidebar.header("Options de filtrage")
new_location = st.sidebar.selectbox("Localisation", df["Localisation"].unique())
new_state = st.sidebar.selectbox("Ville", df["Ville"].unique())
new_investment = st.sidebar.number_input("Somme investie", min_value=0)
new_construction = st.sidebar.selectbox("Construction", df["Construction"].unique())
new_businesstype = st.sidebar.selectbox("Type d'entreprise", df["Type d'entreprise"].unique())
new_earthquake = st.sidebar.selectbox("Séisme", ["Oui", "Non"])
new_flood = st.sidebar.selectbox("Inondation", ["Oui", "Non"])

# Automatically set region based on selected city
new_region = ville_region.get(new_state, "")

# Add a validation button to trigger prediction
validate_button = st.sidebar.button("Valider")

# Predict profitability based on user input when button is clicked
if validate_button:
    if new_investment == 0:
        predicted_rentability = "Erreur : La somme investie ne peut pas être zéro."
    else:
        predicted_rentability = predict_profitability(new_location, new_state, new_investment, new_construction, new_businesstype, new_earthquake, new_flood)

# Display data and analysis
st.header("Data Analysis and Visualisation")
st.write("Données utilisées pour la prédiction:")
st.dataframe(df)

# Display max and min combinations
st.subheader("Combinaison avec la note de rentabilité maximale")
st.write(max_combination)
st.write(f"Note de rentabilité maximale prédite: {predictions[max_index]:.2f}")

st.subheader("Combinaison avec la note de rentabilité minimale")
st.write(min_combination)
st.write(f"Note de rentabilité minimale prédite: {predictions[min_index]:.2f}")

# Display prediction result if validated
if 'predicted_rentability' in locals():
    st.header("Prédiction de la Rentabilité")
    if isinstance(predicted_rentability, float):
        st.write(f"La rentabilité prédite est : {predicted_rentability:.2f}")
    else:
        st.write(predicted_rentability)
        
st.sidebar.image("logo1.png",caption="")
