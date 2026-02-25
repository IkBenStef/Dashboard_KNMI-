import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data_loader import load_knmi_data
from stations import station_dict

# =========================================================
# SIDEBAR
st.sidebar.header("Instellingen")

# Station selectie
selected_station_name = st.sidebar.selectbox("Selecteer station",list(station_dict.keys()))
station = station_dict[selected_station_name]

df, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain, z = load_knmi_data(station=station)

# Jaar slider
min_year = int(df_yearly_temp['year'].min())
max_year = int(df_yearly_temp['year'].max())

selected_year_range = st.sidebar.slider(
    "Selecteer jaartal range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter data op jaarrange
df_yearly_temp_filtered = df_yearly_temp[
    (df_yearly_temp['year'] >= selected_year_range[0]) &
    (df_yearly_temp['year'] <= selected_year_range[1])
]

df_yearly_rain_filtered = df_yearly_rain[
    (df_yearly_rain['year'] >= selected_year_range[0]) &
    (df_yearly_rain['year'] <= selected_year_range[1])
]

df_filtered = df[
    (df['year'] >= selected_year_range[0]) &
    (df['year'] <= selected_year_range[1])
]

# =========================================================
# PAGINA

st.set_page_config(page_title="Vergelijking KNMI", layout="wide")
st.header(f"Jaarlijkse temperatuur & neerslag - {selected_station_name}")


# Lijn + Bar dubbele y-as
fig = go.Figure()

# Temperatuur (lijn)
fig.add_trace(go.Scatter(
    x=df_yearly_temp_filtered['year'],
    y=df_yearly_temp_filtered['Temperatuur_C'],
    mode='lines+markers',
    name='Gem. temperatuur (°C)',
    yaxis='y1'
))

# Neerslag (bar)
fig.add_trace(go.Bar(
    x=df_yearly_rain_filtered['year'],
    y=df_yearly_rain_filtered['Neerslag_MM'],
    name='Totale neerslag (mm)',
    yaxis='y2',
    opacity=0.5
))

# Dubbele y-as layout
fig.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis=dict(title="Temperatuur (°C)", side='left'),
    yaxis2=dict(title="Neerslag (mm)", overlaying='y', side='right'),
    title=f"Temperatuur vs neerslag per jaar - {selected_station_name}"
)

st.plotly_chart(fig, use_container_width=True)

# Correlatieplot temperatuur ↔ neerslag
st.header("Correlatie temperatuur <-> neerslag (jaarlijks)")
st.divider()

fig_corr = px.scatter(
    df_filtered,
    x='Temperatuur_C',
    y='Neerslag_MM',
    opacity=0.7,
    title=f"Temperatuur vs Neerslag ({selected_year_range[0]}-{selected_year_range[1]})"
)

st.plotly_chart(fig_corr, use_container_width=True)
