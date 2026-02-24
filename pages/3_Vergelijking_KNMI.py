import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data_loader import load_knmi_data
from stations import station_dict

st.set_page_config(page_title="Vergelijking KNMI", layout="wide")

# Station selectie
selected_station_name = st.selectbox(
    "Selecteer station",
    list(station_dict.keys())
)
station = station_dict[selected_station_name]

df, df_yearly, df_monthly, df_yearly_rain, z = load_knmi_data(station=station)
st.header(f"Jaarlijkse temperatuur & neerslag - {selected_station_name}")

fig = go.Figure()

# Temperatuur (lijn)
fig.add_trace(go.Scatter(
    x=df_yearly['year'],
    y=df_yearly['Temperatuur_C'],
    mode='lines+markers',
    name='Gem. temperatuur (°C)',
    yaxis='y1'
))

# Neerslag (bar)
fig.add_trace(go.Scatter(
    x=df_yearly_rain['year'],
    y=df_yearly_rain['Neerslag_MM'],
    name='Totale neerslag (mm)',
    yaxis='y2',
    opacity=0.5
))

# Dubbele y-as
fig.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis=dict(title="Temperatuur (°C)", side='left'),
    yaxis2=dict(title="Neerslag (mm)", overlaying='y', side='right'),
    title=f"Temperatuur vs neerslag per jaar - {selected_station_name}"
)

st.plotly_chart(fig, use_container_width=True)
st.header("Correlatie temperatuur ↔ neerslag (jaarlijks)")

st.divider()
fig = px.scatter(
    df,
    x='Temperatuur_C',
    y='Neerslag_MM',
    opacity=0.7,
    title="Temperatuur vs Neerslag"
)
st.plotly_chart(fig, use_container_width=True)
