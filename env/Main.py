import streamlit as st
import pandas as pd
import streamlit.components.v1 as stc
import plotly.express as px
import time
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
from streamlit_extras.metric_cards import style_metric_cards
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go

# Page behavior
st.set_page_config(page_title="Analyse Descriptive", page_icon="🌎", layout="wide")

# Remove default theme
theme_plotly = None  # None or streamlit

# CSS Style
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load Excel file
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# Sidebar filters
st.sidebar.header("Faire des filtres ici :")
region = st.sidebar.multiselect(
    "Sélectionner la région:",
    options=df["Région"].unique(),
    default=df["Région"].unique()
)

# Filter cities based on selected regions
filtered_cities = df[df["Région"].isin(region)]["Ville"].unique()
ville = st.sidebar.multiselect(
    "Sélectionner la Ville:",
    options=filtered_cities,
    default=filtered_cities
)

location = st.sidebar.multiselect(
    "Sélectionner la Localisation:",
    options=df["Localisation"].unique(),
    default=df["Localisation"].unique(),
)
construction = st.sidebar.multiselect(
    "Sélectionner le type de construction:",
    options=df["Construction"].unique(),
    default=df["Construction"].unique()
)
seisme = st.sidebar.radio(
    "La ville connaît des séismes:",
    options=["Oui", "Non"]
)

inondation = st.sidebar.radio(
    "La ville connaît des inondations:",
    options=["Oui", "Non"]
)

# Filter dataframe based on selections
df_selection = df.query(
    "Région == @region & Localisation == @location & Construction == @construction & Séisme == @seisme & Inondation == @inondation & Ville == @ville"
)

# Method/function
def HomePage():
    # 1. print dataframe
    with st.expander("🧭 My database"):
        shwdata = st.multiselect('Filtre :', df_selection.columns, default=['Localisation', 'Ville', 'Région', 'Somme investie', 'Construction', 'Type d\'entreprise', 'Séisme', 'Inondation', 'Rentabilité'])
        st.dataframe(df_selection[shwdata], use_container_width=True)

    # 2. compute top Analytics
    total_investment = float(df_selection['Somme investie'].sum())
    investment_mode = df_selection['Somme investie'].mode()
    if not investment_mode.empty:
        investment_mode = float(investment_mode[0])
    else:
        investment_mode = float('nan')

    investment_mean = float(df_selection['Somme investie'].mean())
    investment_median = float(df_selection['Somme investie'].median())
    rating = float(df_selection['Rentabilité'].sum())

    # 3. columns
    total1, total2, total3, total4, total5 = st.columns(5, gap='small')
    with total1:
        st.info('Total investi', icon="💰")
        st.metric(label='Somme', value=f"{total_investment:,.0f}")
    with total2:
        st.info('La plus fréquente', icon="💰")
        st.metric(label='Mode', value=f"{investment_mode:,.0f}")
    with total3:
        st.info('Moyenne investie', icon="💰")
        st.metric(label='Moyenne', value=f"{investment_mean:,.0f}")
    with total4:
        st.info('Marge sur inves...', icon="💰")
        st.metric(label='Médiane', value=f"{investment_median:,.0f}")
    with total5:
        st.info('Rentabilité', icon="💰")
        st.metric(label='Rentabilité', value=numerize(rating), help=f"""Rentabilité totale: {rating}""")
    style_metric_cards(background_color="#000000", border_left_color="#686664", border_color="#000000", box_shadow="#F71938")

# Graphs
def Graphs():
    total_investments = int(df_selection["Somme investie"].sum())
    average_rating = round(df_selection["Rentabilité"].mean(), 1)
    star_rating = ":star:" * int(round(average_rating, 0))
    average_investment = round(df_selection["Somme investie"].mean(), 2)

    # 1. simple bar graph
    investment_by_businessType = (
        df_selection.groupby(by=["Type d'entreprise"]).count()[["Somme investie"]].sort_values(by="Somme investie")
    )
    fig_investment = px.bar(
        investment_by_businessType,
        x="Somme investie",
        y=investment_by_businessType.index,
        orientation="h",
        title="Investissement par type d'entreprise",
        color_discrete_sequence=["#0083B8"] * len(investment_by_businessType),
        template="plotly_white",
    )

    fig_investment.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    # 2. simple line graph
    investment_by_state = df_selection.groupby(by=["Ville"]).count()[["Somme investie"]]
    fig_state = px.line(
        investment_by_state,
        x=investment_by_state.index,
        orientation="v",
        y="Somme investie",
        title="Investissement par région ",
        color_discrete_sequence=["#0083B8"] * len(investment_by_state),
        template="plotly_white",
    )
    fig_state.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )

    left_column, right_column, center = st.columns(3)
    left_column.plotly_chart(fig_state, use_container_width=True)
    right_column.plotly_chart(fig_investment, use_container_width=True)

    # Pie chart
    with center:
        fig = px.pie(df_selection, values='Rentabilité', names='Ville', title='Rentabilité en fonction des villes')
        fig.update_layout(legend_title="Villes", legend_y=0.9)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

# Progress Bar
def ProgressBar():
    st.markdown("""<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""", unsafe_allow_html=True)
    target = 2480758680
    current = df_selection['Somme investie'].sum()
    percent = round((current / target * 100))
    my_bar = st.progress(0)

    if percent > 100:
        st.subheader("Chargement complet")
    else:
        st.write("Représente ", percent, " % ", " de la somme totale des investissements : ", (format(target, ',d')), " FCFA")
        for percent_complete in range(percent):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1, text="Pourcentage chargé")

# Side Bar
def sideBar():
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["Accueil", "Progression"],
            icons=["house", "eye"],
            menu_icon="cast",  # option
            default_index=0,  # option
        )
    if selected == "Accueil":
        try:
            if df_selection.empty:
                st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
            else:
                HomePage()
                Graphs()
        except Exception as e:
            st.warning(f"Une erreur est survenue: {e}")
    if selected == "Progression":
        try:
            if df_selection.empty:
                st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
            else:
                ProgressBar()
                Graphs()
        except Exception as e:
            st.warning(f"Une erreur est survenue: {e}")

# Print side bar
sideBar()
st.sidebar.image("logo1.png", caption="")

st.subheader('EXPLORATION DES BOITES A MOUSTACHES')
#feature_x = st.selectbox('Select feature for x Qualitative data', df_selection.select_dtypes("object").columns)
feature_y = st.selectbox('Selectionner la colonne selon laquelle filtrer', df_selection.select_dtypes("number").columns)
fig2 = go.Figure(
    data=[go.Box(x=df["Type d'entreprise"], y=df[feature_y])],
    layout=go.Layout(
        title=go.layout.Title(text="BOITES A MOUSTACHES DES TYPES D'ENTREPRISES"),
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Set plot background color to transparent
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Set paper background color to transparent
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Show x-axis grid and set its color
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Show y-axis grid and set its color
        font=dict(color='#cecdcd'),  # Set text color to black
    )
)
# Display the Plotly figure using Streamlit
st.plotly_chart(fig2, use_container_width=True)

#theme
hide_st_style=""" 
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

footer = """<style>
a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
height:5%;
bottom: 0;
width: 100%;
background-color: #243946;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Développé avec Streamlit par Hans Ariel <a style='display: block; text-align: center;' href="https://www.heflin.dev/" target="_blank">Samir.s.s</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
