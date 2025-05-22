import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide", page_title="Monitor pogodowy")

# Automatyczne odświeżanie co 10 sek.
st_autorefresh(interval=10 * 1000, key="data_refresh")

# Funkcja do wczytywania danych JSON
def load_data(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".json")]
    if not files:
        return pd.DataFrame()
    try:
        return pd.concat((pd.read_json(f, lines=True) for f in files), ignore_index=True)
    except ValueError:
        return pd.DataFrame()

# Konwersja timestamp na datę
def convert_timestamps(df):
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    if "alert_issued_at" in df.columns:
        df["alert_issued_at"] = pd.to_datetime(df["alert_issued_at"])
    return df

# Załaduj dane
all_weather = convert_timestamps(load_data("data/all_weather"))
anomalies = convert_timestamps(load_data("data/anomalies"))
alerts = convert_timestamps(load_data("data/alerts"))

# Tłumaczenie nazw kolumn
COLUMN_TRANSLATIONS = {
    "city": "Miasto",
    "timestamp": "Czas pomiaru",
    "temp": "Temperatura [°C]",
    "pressure": "Ciśnienie [hPa]",
    "humidity": "Wilgotność [%]",
    "condition": "Warunki pogodowe",
    "alert_24h": "Alert 24h",
    "anomaly_reason": "Przyczyna anomalii",
    "alert_issued_at": "Data ogłoszenia alertu",
    "lat": "Szerokość geograficzna [°]",
    "lon": "Długość geograficzna [°]"
}

# Tłumaczenie przyczyn anomalii
ANOMALY_REASON_TRANSLATIONS = {
    "temperature_too_low": "Zbyt niska temperatura",
    "temperature_too_high": "Zbyt wysoka temperatura",
    "storm_condition": "Warunki burzowe"
}

# Zastosuj tłumaczenia przyczyn
if "anomaly_reason" in anomalies.columns:
    anomalies["anomaly_reason"] = anomalies["anomaly_reason"].replace(ANOMALY_REASON_TRANSLATIONS)

# UI – tytuł i kolumny
st.title("🌤️ Monitor pogodowy")

tab1, tab2, tab3 = st.tabs(["🌍 Mapa miast", "⚠️ Anomalie pogodowe", "📢 Alerty"])

with tab1:
    if not all_weather.empty and {"lat", "lon"}.issubset(all_weather.columns):
        # Usuwanie duplikatów – ostatni wpis na miasto
        latest_weather = all_weather.sort_values("timestamp").drop_duplicates("city", keep="last")

        city = st.selectbox("Wybierz miasto", sorted(latest_weather["city"].unique()))
        city_data = latest_weather[latest_weather["city"] == city]

        st.map(city_data.rename(columns={"lat": "latitude", "lon": "longitude"}))
        st.dataframe(city_data.rename(columns=COLUMN_TRANSLATIONS), use_container_width=True)
    else:
        st.warning("Brak danych pogodowych z koordynatami.")

with tab2:
    if not anomalies.empty:
        st.dataframe(anomalies.rename(columns=COLUMN_TRANSLATIONS), use_container_width=True)
    else:
        st.info("Brak wykrytych anomalii pogodowych.")

with tab3:
    if not alerts.empty:
        st.dataframe(alerts.rename(columns=COLUMN_TRANSLATIONS), use_container_width=True)
    else:
        st.info("Brak aktywnych alertów pogodowych.")
