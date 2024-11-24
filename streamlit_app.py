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

activity = st.Page(
  'people/activity_report.py', 
  title = 'Activity Report',  
  icon=":material/motion_sensor_active:",
  default=False
)

inactive = st.Page(
  'people/inactive_report.py', 
  title = 'Inactive Report',  
  icon=":material/person_remove:",
  default=False
)

pdq = st.Page(
  'people/people_data_quality.py', 
  title = 'Data Quality Report',  
  icon=":material/equalizer:",
  default=False
)

# group report
group_attendance_report = st.Page(
  'groups/group_attendance_report.py', 
  title = 'Group Attendance Report',  
  icon=":material/groups:",
  default=False
)


# navigation 
pg = st.navigation(
        {
            "Home": [home],
            "Giving Analytics": [yoy_giving, fee_giving, forecast_giving, donor_risk],
            "Headcount Analytics": [headcount],
            "People Analytics": [people, activity, inactive, pdq],
            "Group Analytics": [group_attendance_report]
        }
    )

pg.run()
