# dit is tijdelijk, wordt vervangen door ander
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Jouw functie importeren
from data_loader import load_knmi_data

st.title("KNMI Temperatuur Voorspeller")

# ===============================
# Data laden
# ===============================
df_meteorologisch, df_yearly_temp, df_monthly_temp, df_monthly_rain, df_yearly_rain = load_knmi_data()

max_year = df_yearly_temp["year"].max()

st.write(f"Maximaal jaar in dataset: {max_year}")

# ===============================
# Input toekomstig jaar
# ===============================
future_year = st.number_input(
    "Voer een toekomstig jaartal in:",
    min_value=int(max_year + 1),
    value=int(max_year + 5)
)

# ===============================
# Jaarlijkse voorspelling
# ===============================

# Lineaire regressie met numpy
coefficients = np.polyfit(df_yearly_temp["year"], df_yearly_temp["Temperatuur_C"], 1)
slope, intercept = coefficients

def predict(year):
    return slope * year + intercept

years_range = pd.DataFrame({"year": np.arange(2000, future_year + 1)})
years_range["prediction"] = years_range["year"].apply(predict)

df_actual = df_yearly_temp[df_yearly_temp["year"] >= 2000]
df_pred_future = years_range[years_range["year"] > max_year]

fig_line = px.line(
    df_actual,
    x="year",
    y="Temperatuur_C",
    title="Gemiddelde Jaarlijkse Temperatuur (2000 - toekomst)",
    name='Historisch'
)

fig_line.add_scatter(
    x=df_pred_future["year"],
    y=df_pred_future["prediction"],
    mode="lines",
    name="Voorspelling",
    line=dict(color="red")
)

st.plotly_chart(fig_line, use_container_width=True)

st.subheader(f"Voorspelde gemiddelde temperatuur in {future_year}:")
st.write(f"{predict(future_year):.2f} °C")

# ===============================
# Maandelijkse vergelijking
# ===============================

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
