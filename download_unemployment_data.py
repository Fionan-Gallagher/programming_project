import wbdata
import pandas as pd
import datetime as dt
import os

# List of countries
countries = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE", "GB", "US",
]

indicator = {"SL.UEM.TOTL.ZS": "Unemployment rate (%)"}

end_date = dt.datetime.now()
start_date = dt.datetime(end_date.year - 34, 1, 1)

print(f"Downloading unemployment data from {start_date.year} to {end_date.year}...")

df = wbdata.get_dataframe(
    indicator,
    country=countries,
    date=(start_date, end_date),
)

# Reset index and clean up
df = df.reset_index().rename(columns={"country": "country_code", "date": "Year"})
df["Year"] = pd.to_datetime(df["Year"], errors="coerce").dt.year
df = df.dropna(subset=["Unemployment rate (%)"])

# Create folder and save CSV
os.makedirs("data", exist_ok=True)
output_path = os.path.join("data", "unemployment.csv")
df.to_csv(output_path, index=False)

print(f"✅ Done! Saved to {output_path}")
