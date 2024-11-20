import streamlit as st
  
home_page = st.Page(
  'home_page/home_page.py', title = 'Home', icon=":material/home:", default=True
)



pg = st.navigation(
        {
            " ": [home_page],

        }
    )

pg.run()
