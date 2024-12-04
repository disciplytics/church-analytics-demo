
# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# connect to snowflake
conn = st.connection("snowflake")

# Page Parameters
st.header("Feature Requests")

st.write('Is the current app not meeting all your needs? Make a feature request below and we will review it.')


with st.form("feature_request_form"):
    st.write("Feature Request")
    slider_val = st.slider("Form slider")
    checkbox_val = st.checkbox("Form checkbox")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("slider", slider_val, "checkbox", checkbox_val)

risk_df = conn.query('''SELECT * FROM ANALYTICS.DONOR_RISK''', ttl=0)
