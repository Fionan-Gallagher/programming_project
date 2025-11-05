import streamlit as st
import pandas as pd
import wbdata
import datetime
import plotly.express as px

def show():
    st.header("Unemployment Rate (% of Total Labor Force)")

    # --- Country options (all EU + UK + US) ---
    countries = {
        "Austria": "AT",
        "Belgium": "BE",
        "Bulgaria": "BG",
        "Croatia": "HR",
        "Cyprus": "CY",
        "Czech Republic": "CZ",
        "Denmark": "DK",
        "Estonia": "EE",
        "Finland": "FI",
        "France": "FR",
        "Germany": "DE",
        "Greece": "GR",
        "Hungary": "HU",
        "Ireland": "IE",
        "Italy": "IT",
        "Latvia": "LV",
        "Lithuania": "LT",
        "Luxembourg": "LU",
        "Malta": "MT",
        "Netherlands": "NL",
        "Poland": "PL",
        "Portugal": "PT",
        "Romania": "RO",
        "Slovakia": "SK",
        "Slovenia": "SI",
        "Spain": "ES",
        "Sweden": "SE",
        "United Kingdom": "GB",
        "United States": "US",
    }

    # --- Date range (last 10 years) ---
    end_date = datetime.datetime.now()
    start_date = datetime.datetime(end_date.year - 10, 1, 1)

    # --- User selector ---
    country_name = st.selectbox("Select a country:", list(countries.keys()))
    country_code = countries[country_name]

    st.write(f"Fetching unemployment data for **{country_name}**...")

    # --- Fetch World Bank data ---
    df = wbdata.get_dataframe(
        {"SL.UEM.TOTL.ZS": "Unemployment rate (%)"},
        country=country_code,
        date=(start_date, end_date)
    ).sort_index()

    # --- Plotting the data ---
    if not df.empty:
        fig = px.line(
            df,
            x=df.index,
            y="Unemployment rate (%)",
            title=f"Unemployment Rate in {country_name} ({start_date.year}–{end_date.year})",
            labels={"x": "Year", "Unemployment rate (%)": "Unemployment Rate (%)"},
        )
        st.plotly_chart(fig, use_container_width=True)

        latest_value = df["Unemployment rate (%)"].iloc[-1]
        latest_year = str(df.index[-1])  # convert to string safely
        st.write(f"**Latest ({latest_year}):** {latest_value:.2f}%")

    else:
        st.warning("No data available for this selection.")


