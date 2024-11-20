import streamlit as st
  
home_page = st.Page(
  'pages/1_Giving.py', title = 'Giving Report', icon=":material/money:", default=True
)



pg = st.navigation(
        {
            " ": [home_page],

        }
    )

pg.run()
