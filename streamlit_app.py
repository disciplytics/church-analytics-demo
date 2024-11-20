import streamlit as st
  
giving = st.Page(
  'pages/1_Giving.py', title = 'Giving Report',  default=False
)

headcount = st.Page(
  'pages/2_Headcount.py', title = 'Headcount Report', default=False
)



pg = st.navigation(
        {
            " ": [giving, headcount],

        }
    )

pg.run()
