
import streamlit as st
import pandas as pd
import wbdata
import datetime
import plotly.express as px


def show():
    st.header("Unemployment Rate (% of Total Labor Force)")

    #  Country options (all EU + UK + US) 
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

    # Date range (last 34 years)
    end_date = datetime.datetime.now()
    start_date = datetime.datetime(end_date.year - 34, 1, 1)

    # User selector
    country_name = st.selectbox("Select a country:", list(countries.keys()))
    country_code = countries[country_name]

    st.write(f"Fetching unemployment data for **{country_name}**...")

    # --- Fetch World Bank Data for selected country and EU average ---

    # Exclude UK and US from EU average
    eu_countries = [v for k, v in countries.items() if k not in ["United Kingdom", "United States"]]

    # Fetch World Bank data for the selected country
    df = wbdata.get_dataframe(
        {"SL.UEM.TOTL.ZS": "Unemployment rate (%)"},
        country=country_code,
        date=(start_date, end_date)
    ).sort_index()

    # Fetch data for EU countries
    eu_data = wbdata.get_dataframe(
        {"SL.UEM.TOTL.ZS": "Unemployment rate (%)"},
        country=eu_countries,
        date=(start_date, end_date)
    ).sort_index()

    # --- Calculate EU Average ---
    eu_data = eu_data.reset_index()  # make 'date' a column
    eu_data['date'] = pd.to_datetime(eu_data['date'], errors='coerce')  # ensure datetime type
    eu_data = eu_data.dropna(subset=['date'])  # drop invalid rows
    eu_data['Year'] = eu_data['date'].dt.year  # extract year

    # Average unemployment across EU countries by year
    eu_avg = eu_data.groupby('Year')["Unemployment rate (%)"].mean().dropna()
    eu_avg_df = pd.DataFrame({
        'Year': eu_avg.index,
        'EU Average (%)': eu_avg.values
    })

    # --- Plotting the data ---
    if not df.empty:
        # drop NaNs for summary computations
        df_clean = df.dropna()

        # build the plot
        fig = px.line(
            title=f"Unemployment Rate in {country_name} vs EU Average ({start_date.year}–{end_date.year})",
            labels={"x": "Year", "y": "Unemployment Rate (%)"},
        )

        # --- Add country line manually so it always has the right legend label ---
        fig.add_scatter(
            x=df.index,
            y=df["Unemployment rate (%)"],
            mode="lines+markers",
            name=country_name,  
            line=dict(color="steelblue", width=3),
            hovertemplate="Year: %{x|%Y}<br>Unemployment: %{y:.2f}%<extra></extra>"
        )

        # --- Add EU Average Line ---
        fig.add_scatter(
            x=eu_avg_df['Year'],
            y=eu_avg_df['EU Average (%)'],
            mode="lines",
            name="EU Average",
            line=dict(color="orange", width=3, dash="dash"),
            hovertemplate="Year: %{x}<br>EU Average: %{y:.2f}%<extra></extra>"
        )

        # --- Format only the main country's line (not all traces) ---
        fig.update_traces(
            selector=dict(name="Unemployment rate (%)"),
            mode="lines+markers",
            name=country_name,
            line=dict(color="steelblue", width=3),
            hovertemplate="Year: %{x|%Y}<br>Unemployment: %{y:.2f}%<extra></extra>"
        )

        # --- Final layout tweaks ---
        fig.update_layout(
            hovermode="x unified",
            xaxis=dict(tickformat="%Y"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        )

        fig.update_layout(hovermode="x unified", xaxis=dict(tickformat="%Y"))

        # show points and format hover text (year and value)
        fig.update_traces(mode="lines+markers", hovertemplate="Year: %{x|%Y}<br>Unemployment: %{y:.2f}%<extra><extra></extra>")
        fig.update_layout(hovermode="x unified", xaxis=dict(tickformat="%Y"))

        # layout: plot on the left, summary stats on the right
        col_plot, col_stats = st.columns([3, 1])

        with col_plot:
            st.plotly_chart(fig, use_container_width=True)
            # --- Dynamic comparison sentence ---
            try:
                latest_year = int(df.index[-1].year if hasattr(df.index[-1], "year") else str(df.index[-1]))
                country_latest = df["Unemployment rate (%)"].iloc[-1]

                 # match EU average for same year (if available)
                eu_latest = eu_avg_df.loc[eu_avg_df['Year'] == latest_year, 'EU Average (%)']
                if not eu_latest.empty:
                    eu_latest = eu_latest.iloc[0]

                    diff = country_latest - eu_latest
                    relation = "below" if diff < 0 else "above" if diff > 0 else "equal to"

                    st.markdown(
                        f" In **{latest_year}**, **{country_name}**’s unemployment rate "
                        f"was **{abs(diff):.2f} percentage points {relation}** the EU average "
                        f"({country_latest:.2f}% vs {eu_latest:.2f}%)."
                )
            except Exception as e:
                st.caption("Comparison unavailable for this year.")







   





        with col_stats:
            if not df_clean.empty:
                series = df_clean["Unemployment rate (%)"]
                latest_value = series.iloc[-1]
                earliest_value = series.iloc[0]
                change_pp = latest_value - earliest_value
                change_pct = (change_pp / earliest_value * 100) if earliest_value != 0 else float('inf')

                mean_val = series.mean()
                median_val = series.median()
                std_val = series.std()
                min_val = series.min()
                max_val = series.max()
                min_year = str(series.idxmin())
                max_year = str(series.idxmax())

                # top-line metrics
                delta_display = f"{change_pp:+.2f} pp"
                if change_pct is not None and change_pct != float('inf'):
                    delta_display += f" ({change_pct:+.1f}%)"

                st.metric(
                    label=f"Latest ({str(series.index[-1])})",
                    value=f"{latest_value:.2f}%",
                    delta=delta_display
                )

                # summary table
                stats = {
                    "Mean": f"{mean_val:.2f}%",
                    "Median": f"{median_val:.2f}%",
                    "Std Dev": f"{std_val:.2f}",
                    "Min": f"{min_val:.2f}% ({min_year})",
                    "Max": f"{max_val:.2f}% ({max_year})",
                }
                st.write("Summary Statistics")
                st.table(pd.Series(stats).to_frame("Value"))
            else:
                st.warning("No non-missing observations to compute summary statistics.")

        latest_value = df["Unemployment rate (%)"].iloc[-1]
        latest_year = str(df.index[-1])  # convert to string safely
        st.write(f"**Latest ({latest_year}):** {latest_value:.2f}%")

    else:
        st.warning("No data available for this selection.")



