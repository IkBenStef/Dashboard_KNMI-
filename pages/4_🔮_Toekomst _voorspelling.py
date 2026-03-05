# dit is tijdelijk, wordt vervangen door ander
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_knmi_data
from data_loader import get_cbsodata_energie

st.title("KNMI Temperatuur Voorspeller")

# ===================================================== Data laden
df_meteorologisch, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain = load_knmi_data()

max_year = df_yearly_temp["year"].max()

st.write(f"Maximaal jaar in dataset: {max_year}")

# ===================================================== Input toekomstig jaar
future_year = st.number_input(
    "Voer een toekomstig jaartal in:",
    min_value=int(max_year + 1),
    value=int(max_year + 5)
)

# ===================================================== Jaarlijkse voorspelling

# Lineaire regressie met numpy
coefficients = np.polyfit(df_yearly_temp["year"], df_yearly_temp["Temperatuur_C"], 1)
slope, intercept = coefficients

def predict(year):
    return slope * year + intercept

years_range = pd.DataFrame({"year": np.arange(2000, future_year + 1)})
years_range["prediction"] = years_range["year"].apply(predict)

df_actual = df_yearly_temp[df_yearly_temp["year"] >= 2000]
df_pred_future = years_range[years_range["year"] > max_year]

fig_line = go.Figure()
# De Historische lijn
fig_line.add_trace(go.Scatter(
    x=df_actual["year"],
    y=df_actual["Temperatuur_C"],
    mode="lines",
    name="Historisch",
    line=dict(color="#3656f6")
))
# De Voorspelling lijn
fig_line.add_trace(go.Scatter(
    x=df_pred_future["year"],
    y=df_pred_future["prediction"],
    mode="lines",
    name="Voorspelling",
    line=dict(color="#e5344b", dash="dash")
))
fig_line.update_layout(
    title="Gemiddelde Jaarlijkse Temperatuur (2000 - toekomst)",
    xaxis_title="Jaar",
    yaxis_title="Temperatuur (°C)"
)
st.plotly_chart(fig_line, use_container_width=True)

st.subheader(f"Voorspelde gemiddelde temperatuur in {future_year}:")
st.write(f"{predict(future_year):.2f} °C")

# =================================================== Maandelijkse vergelijking

st.subheader("Maandelijkse temperatuur vergelijking")

# Vergelijkingsjaar kiezen (standaard max_year)
compare_year = st.selectbox(
    "Kies een jaar om mee te vergelijken:",
    options=sorted(df_yearly_temp["year"].unique()),
    index=len(df_yearly_temp["year"].unique()) - 1
)

# Maandnamen
month_names = {
    1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
    9: "September", 10: "Oktober", 11: "November", 12: "December"
}

monthly_data = []

for month in range(1, 13):
    # Historische data voor maand
    df_month = df_monthly_temp[df_monthly_temp["month"] == month]

    # Regressie per maand
    coeff = np.polyfit(df_month["year"], df_month["Temperatuur_C"], 1)
    slope_m, intercept_m = coeff
    prediction = slope_m * future_year + intercept_m

    # Werkelijke waarde van gekozen vergelijkingsjaar
    actual_value = df_monthly_temp[
        (df_monthly_temp["year"] == compare_year) &
        (df_monthly_temp["month"] == month)
    ]["Temperatuur_C"]

    if not actual_value.empty:
        actual_value = actual_value.values[0]
    else:
        actual_value = None

    monthly_data.append({
        "Maand": month_names[month],
        "Type": f"Vergelijkingsjaar ({compare_year})",
        "Temperatuur": actual_value
    })

    monthly_data.append({
        "Maand": month_names[month],
        "Type": f"Voorspelling ({future_year})",
        "Temperatuur": prediction
    })

df_month_plot = pd.DataFrame(monthly_data)

fig_bar = px.bar(
    df_month_plot,
    x="Maand",
    y="Temperatuur",
    color="Type",
    barmode="group",
    title=f"Maandelijkse temperatuur: {compare_year} vs voorspelling {future_year}",
    color_discrete_map={
        f"Vergelijkingsjaar ({compare_year})": "#3656f6",
        f"Voorspelling ({future_year})": "#e5344b"
    }
)

st.plotly_chart(fig_bar, use_container_width=True)
# ============================================================
# ENERGIEVERBRUIK (CBS) – zelfde structuur als temperatuur
# ============================================================

st.header("Energieverbruik Voorspeller (CBS)")

df_energie = get_cbsodata_energie()

# -----------------------------
# Zelfde filtering als in jouw andere pagina
# -----------------------------
df_energie = df_energie[~df_energie['Perioden'].str.contains('1e|2e|3e|4e', na=False)]
df_energie = df_energie[df_energie['Perioden'].str.count(' ') == 1]

maand_map = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4,
    "mei": 5, "juni": 6, "juli": 7, "augustus": 8,
    "september": 9, "oktober": 10, "november": 11, "december": 12,
}

df_energie[['jaar', 'maand']] = df_energie['Perioden'].str.split(' ', n=1, expand=True)
df_energie['maand'] = df_energie['maand'].str.strip()

df_energie['date'] = pd.to_datetime({
    'year': df_energie['jaar'].astype(int),
    'month': df_energie['maand'].map(maand_map),
    'day': 1
}, errors='coerce')

# -----------------------------
# JAARLIJKSE GEMIDDELDE (zoals temperatuur)
# -----------------------------
df_yearly_energy = (
    df_energie
    .groupby(df_energie['date'].dt.year)['NettoVerbruikBerekend_30']
    .mean()
    .reset_index()
)

df_yearly_energy.columns = ["year", "Energieverbruik"]

max_year_energy = df_yearly_energy["year"].max()

future_year_energy = st.number_input(
    "Voer een toekomstig jaartal in (energie):",
    min_value=int(max_year_energy + 1),
    value=int(max_year_energy + 5),
    key="energy_future"
)

# -----------------------------
# Lineaire regressie (identiek aan temperatuur)
# -----------------------------
coeff_energy = np.polyfit(
    df_yearly_energy["year"],
    df_yearly_energy["Energieverbruik"],
    1
)

slope_energy, intercept_energy = coeff_energy

def predict_energy(year):
    return slope_energy * year + intercept_energy

years_energy = pd.DataFrame({
    "year": np.arange(df_yearly_energy["year"].min(), future_year_energy + 1)
})

years_energy["prediction"] = years_energy["year"].apply(predict_energy)

df_actual_energy = df_yearly_energy[
    df_yearly_energy["year"] >= 2000
]

df_pred_future_energy = years_energy[
    years_energy["year"] > max_year_energy
]

# -----------------------------
# Plot (identiek aan temperatuur)
# -----------------------------
fig_energy = px.line(
    df_actual_energy,
    x="year",
    y="Energieverbruik",
    title="Gemiddeld Jaarlijks Netto Energieverbruik (2000 - toekomst)"
)

fig_energy.add_scatter(
    x=df_pred_future_energy["year"],
    y=df_pred_future_energy["prediction"],
    mode="lines",
    name="Voorspelling",
    line=dict(color="red")
)

st.plotly_chart(fig_energy, use_container_width=True)

st.subheader(f"Voorspeld gemiddeld energieverbruik in {future_year_energy}:")
st.write(f"{predict_energy(future_year_energy):,.0f} mln kWh")
# ===================================================
# Maandelijkse energie vergelijking
# ===================================================

st.subheader("Maandelijkse energie vergelijking")

compare_year_energy = st.selectbox(
    "Kies een jaar om energie mee te vergelijken:",
    options=sorted(df_yearly_energy["year"].unique()),
    index=len(df_yearly_energy["year"].unique()) - 1,
    key="energy_compare"
)

month_names = {
    1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
    9: "September", 10: "Oktober", 11: "November", 12: "December"
}

monthly_energy_data = []

for month in range(1, 13):

    df_month = df_energie[df_energie['date'].dt.month == month]

    # Regressie per maand
    coeff = np.polyfit(
        df_month['date'].dt.year,
        df_month['NettoVerbruikBerekend_30'],
        1
    )

    slope_m, intercept_m = coeff
    prediction = slope_m * future_year_energy + intercept_m

    # Werkelijke waarde gekozen jaar
    actual_value = df_energie[
        (df_energie['date'].dt.year == compare_year_energy) &
        (df_energie['date'].dt.month == month)
    ]['NettoVerbruikBerekend_30']

    if not actual_value.empty:
        actual_value = actual_value.values[0]
    else:
        actual_value = None

    monthly_energy_data.append({
        "Maand": month_names[month],
        "Type": f"Vergelijkingsjaar ({compare_year_energy})",
        "Energie": actual_value
    })

    monthly_energy_data.append({
        "Maand": month_names[month],
        "Type": f"Voorspelling ({future_year_energy})",
        "Energie": prediction
    })

df_month_energy_plot = pd.DataFrame(monthly_energy_data)

fig_bar_energy = px.bar(
    df_month_energy_plot,
    x="Maand",
    y="Energie",
    color="Type",
    barmode="group",
    title=f"Maandelijkse energie: {compare_year_energy} vs voorspelling {future_year_energy}",
    color_discrete_map={
        f"Vergelijkingsjaar ({compare_year_energy})": "#3656f6",
        f"Voorspelling ({future_year_energy})": "#e5344b"
    }
)

st.plotly_chart(fig_bar_energy, use_container_width=True)