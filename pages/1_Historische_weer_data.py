import streamlit as st
import plotly.graph_objects as go
from data_loader import load_knmi_data

st.set_page_config(page_title="Historische data", layout="wide")

df_temp, df_yearly, df_monthly, z = load_knmi_data()

# =========================================================
# 1️⃣ JAARGEMIDDELDE MET TREND
# =========================================================

st.header("Jaargemiddelde temperatuur")

min_year = int(df_yearly['year'].min())
max_year = int(df_yearly['year'].max())

selected_year_range = st.slider(
    "Selecteer jaartal range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

df_yearly_filtered = df_yearly[
    (df_yearly['year'] >= selected_year_range[0]) &
    (df_yearly['year'] <= selected_year_range[1])
]

fig_year = go.Figure()

fig_year.add_trace(go.Scatter(
    x=df_yearly_filtered['year'],
    y=df_yearly_filtered['original'],
    mode='lines+markers',
    name='Gemiddelde temperatuur'
))

fig_year.add_trace(go.Scatter(
    x=df_yearly_filtered['year'],
    y=df_yearly_filtered['trend'],
    mode='lines',
    name='Trend',
    line=dict(dash='dash')
))

fig_year.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Gemiddelde temperatuur (°C)",
)

st.plotly_chart(fig_year, use_container_width=True)
st.markdown(f"**Gemiddelde stijging per jaar:** {z[0]:.4f} °C")

st.divider()

# =========================================================
# 2️⃣ GEMIDDELDE PER MAAND (BARPLOT MET JAARSLIDER)
# =========================================================

st.header("Gemiddelde temperatuur per maand")

selected_year_range_month = st.slider(
    "Selecteer jaartal range voor maandgemiddelde",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    key="month_slider"
)

df_monthly_filtered = df_monthly[
    (df_monthly['year'] >= selected_year_range_month[0]) &
    (df_monthly['year'] <= selected_year_range_month[1])
]

df_monthly_avg = df_monthly_filtered.groupby('month')['original'].mean().reset_index()

fig_month_bar = go.Figure()

fig_month_bar.add_trace(go.Bar(
    x=df_monthly_avg['month'],
    y=df_monthly_avg['original'],
    marker=dict(
        color=df_monthly_avg['original'],
        colorscale='Bluered',
        colorbar=dict(title="Waarde")
    ),
    name="Maandgemiddelde"
))

fig_month_bar.update_layout(
    template="plotly_white",
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(1, 13)),
        ticktext=["Jan", "Feb", "Mrt", "Apr", "Mei", "Jun",
                  "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
    ),
    xaxis_title="Maand",
    yaxis_title="Gemiddelde temperatuur (°C)",
)

st.plotly_chart(fig_month_bar, use_container_width=True)

st.divider()

# =========================================================
# 3️⃣ ONTWIKKELING VAN ÉÉN MAAND OVER DE JAREN
# =========================================================

st.header("Ontwikkeling van specifieke maand over de jaren")

maand_namen = {
    1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
    9: "September", 10: "Oktober", 11: "November", 12: "December"
}

selected_month = st.selectbox(
    "Selecteer maand",
    options=list(maand_namen.keys()),
    format_func=lambda x: maand_namen[x],
    index=0  # standaard januari
)

df_selected_month = df_monthly[df_monthly['month'] == selected_month]

fig_month_trend = go.Figure()

fig_month_trend.add_trace(go.Scatter(
    x=df_selected_month['year'],
    y=df_selected_month['original'],
    mode='lines+markers',
    name=maand_namen[selected_month]
))

fig_month_trend.update_layout(
    template="plotly_white",
    xaxis_title="Jaar",
    yaxis_title="Gemiddelde temperatuur (°C)",
)

st.plotly_chart(fig_month_trend, use_container_width=True)
