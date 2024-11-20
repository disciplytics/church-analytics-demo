import streamlit as st
  
giving = st.Page(
  'pages/1_Giving.py', title = 'Giving Report', icon=":material/money:", default=True
)



pg = st.navigation(
        {
            " ": [giving],

        }
    )

pg.run()
