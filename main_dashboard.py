import streamlit as st
from panels import unemployment_panel

st.title("Global Macroeconomics Dashboard")
st.write("Explore global macroeconomic indicators across countries in this interactive dashboard")


# Tabs for each panel
tab1, tab2, tab3, tab4 = st.tabs(["GDP", "Inflation", "Interest Rates", "Unemployment"])
                                  
with tab4:
    unemployment_panel.show()

    










                            
