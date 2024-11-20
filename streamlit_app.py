import streamlit as st

home = st.Page('home.py', title = 'Home',  default=True
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
            "Reports": [giving, headcount, groups, people],

        }
    )

pg.run()
