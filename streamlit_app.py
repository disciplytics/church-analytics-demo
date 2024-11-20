import streamlit as st

home = st.Page(
  'Welcome.py', 
  title = 'Welcome', 
  icon=":material/home:", 
  default=True
)

# giving reports
yoy_giving = st.Page(
  'giving/year_over_year_giving.py', 
  title = 'Year/Year Giving Report',
  icon=":material/paid:",
  default=False
)

fee_giving = st.Page(
  'giving/giving_fees.py', 
  title = 'Giving Fees Report',
  icon=":material/sell:",
  default=False
)

forecast_giving = st.Page(
  'giving/giving_forecasts.py', 
  title = 'Giving Forecast Report',
  icon=":material/query_stats:",
  default=False
)

donor_risk = st.Page(
  'giving/donor_risk.py', 
  title = 'Donor Risk Report',
  icon=":material/health_and_safety:",
  default=False
)

# headcount reports
headcount = st.Page(
  'headcount/headcount.py', 
  title = 'Headcount Report',  
  icon=":material/group_add:",
  default=False
)

# people report
people = st.Page(
  'people/people_report.py', 
  title = 'People Report',  
  icon=":material/person:",
  default=False
)




# navigation 
pg = st.navigation(
        {
            " ": [home],
            "Giving Analytics": [yoy_giving, fee_giving, forecast_giving, donor_risk],
            "Headcount Analytics": [headcount],
            "People Analytics": [people]

        }
    )

pg.run()
