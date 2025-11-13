# importing libraries
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
@st.cache_data
def load_unemployment_data():
    df = pd.read_csv("data/unemployment.csv")
    return df
 


# function to display unemployment panel
def show():
    st.header("Unemployment Rate (% of Total Labor Force)")

    # List of counntries - using all EU countires and the US and UK
    countries = [
        "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus",
        "Czech Republic", "Denmark", "Estonia", "Finland", "France",
        "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia",
        "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland",
        "Portugal", "Romania", "Slovakia", "Slovenia", "Spain",
        "Sweden", "United Kingdom", "United States",
    ]

    # Date range (last 34 years)
    end_date = datetime.datetime.now()
    start_date = datetime.datetime(end_date.year - 34, 1, 1)

    # User selector for country
    country_name = st.selectbox("Select a country:", countries)
    st.write(f"Fetching unemployment data for **{country_name}**...")

    # Load data from the local CSV
    data = load_unemployment_data()

    # adjustment:  filtering counrties by name, not by their two letter code
    df = data[data["country_code"] == country_name].copy()

    # Exclude UK and US from EU average
    eu_countries = [c for c in countries if c not in ["United Kingdom", "United States"]]
    eu_data = data[data["country_code"].isin(eu_countries)].copy()

    # Making sure Year is an int
    eu_data = eu_data.dropna(subset=["Year"])
    eu_data["Year"] = eu_data["Year"].astype(int)

    # Average unemployment across EU countries by year
    eu_avg = eu_data.groupby("Year")["Unemployment rate (%)"].mean().dropna()
    eu_avg_df = pd.DataFrame({
        "Year": eu_avg.index,
        "EU Average (%)": eu_avg.values
    })

    # Plotting (and cleaning the data) 
    if not df.empty:
        df_clean = df.dropna()

        fig = px.line(
            title=f"Unemployment Rate in {country_name} vs EU Average ({start_date.year}–{end_date.year})",
            labels={"x": "Year", "y": "Unemployment Rate (%)"},
        )

        fig.add_scatter(
            x=df["Year"],
            y=df["Unemployment rate (%)"],
            mode="lines+markers",
            name=country_name,
            line=dict(color="steelblue", width=3),
            hovertemplate="Year: %{x}<br>Unemployment: %{y:.2f}%<extra></extra>"
        )

        fig.add_scatter(
            x=eu_avg_df["Year"],
            y=eu_avg_df["EU Average (%)"],
            mode="lines",
            name="EU Average",
            line=dict(color="orange", width=3, dash="dash"),
            hovertemplate="Year: %{x}<br>EU Average: %{y:.2f}%<extra></extra>"
        )
        # adding a hovering feature on the graph
        fig.update_layout(
            hovermode="x unified",
            xaxis=dict(tickformat="%Y"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        )

        col_plot, col_stats = st.columns([3, 1])

        with col_plot:
            st.plotly_chart(fig, use_container_width=True)

            # Dynamic comparison between unemployment for Country and EU average
            try:
                latest_year = int(df["Year"].iloc[-1])
                country_latest = df["Unemployment rate (%)"].iloc[-1]
                eu_latest_row = eu_avg_df.loc[eu_avg_df["Year"] == latest_year, "EU Average (%)"]

                if not eu_latest_row.empty:
                    eu_latest = eu_latest_row.iloc[0]
                    diff = country_latest - eu_latest
                    relation = "below" if diff < 0 else "above" if diff > 0 else "equal to"

                    st.markdown(
                        f"In **{latest_year}**, **{country_name}**’s unemployment rate "
                        f"was **{abs(diff):.2f} percentage points {relation}** the EU average "
                        f"({country_latest:.2f}% vs {eu_latest:.2f}%)."
                    )
            except Exception:
                st.caption("Comparison unavailable for this year.")
            # getting summary statistics
        with col_stats:
            if not df_clean.empty:
                series = df_clean["Unemployment rate (%)"]
                latest_value = series.iloc[-1]
                earliest_value = series.iloc[0]
                change_pp = latest_value - earliest_value
                change_pct = (change_pp / earliest_value * 100) if earliest_value != 0 else float("inf")

                mean_val = series.mean()
                median_val = series.median()
                std_val = series.std()
                min_val = series.min()
                max_val = series.max()
                min_year = int(df_clean.loc[series.idxmin(), "Year"])
                max_year = int(df_clean.loc[series.idxmax(), "Year"])

                delta_display = f"{change_pp:+.2f} pp"
                if change_pct not in [None, float("inf")]:
                    delta_display += f" ({change_pct:+.1f}%)"

                st.metric(
                    label=f"Latest ({latest_year})",
                    value=f"{latest_value:.2f}%",
                    delta=delta_display
                )

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
        latest_year = int(df["Year"].iloc[-1])
        st.write(f"**Latest ({latest_year}):** {latest_value:.2f}%")

    else:
        st.warning("No data available for this selection.")

        