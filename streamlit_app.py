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


giving = st.Page(
  'pages/1_Giving.py', title = 'Giving Report',  default=False
)

headcount = st.Page(
  'pages/2_Headcount.py', title = 'Headcount Report', default=False
)

groups = st.Page(
  'pages/3_Groups.py', title = 'Groups Report', default=False
)


people = st.Page(
  'pages/4_People.py', title = 'People Report', default=False
)



pg = st.navigation(
        {
            " ": [home],
            "Giving Report": [yoy_giving],
            "Reports": [giving, headcount, groups, people],

        }
    )

pg.run()
