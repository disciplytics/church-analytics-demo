
# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# connect to snowflake
conn = st.connection("snowflake")

# Page Parameters
st.header("Donor Risk Report")

risk_df = conn.query('''SELECT * FROM ANALYTICS.DONOR_RISK''', ttl=0)
    
risk_df = risk_df.rename(columns={
        'HOUSEHOLD_PRIMARY_CONTACT': 'Primary Contact',
        'ADDRESS': 'Addresss',
        'PHONE': 'Phone',
        'EMAIL': 'Email',
        'DAYS_SINCE_LAST_DONATION': '# of Days Since Last Donation',
        'LAST_DONTATION_DATE': 'Last Donation Date',
        'AVG_DAYS_BETWEEN_DONATIONS': 'Avg # of Days Between a Donations',
        'NUMBER_OF_DONATIONS': '# of Donations in Last 365 Days',
        'DONOR_RISK_RATING': 'Donor Risk Rating'})
    
risk_df = risk_df.set_index(['Primary Contact'])

# rename ratings for front end

risk_df.loc[risk_df['Donor Risk Rating'] == 'DONOR_SAFE', 'Donor Risk Rating'] ='Safe'
risk_df.loc[risk_df['Donor Risk Rating'] == 'DONOR_WARNING', 'Donor Risk Rating'] ='Warning'
risk_df.loc[risk_df['Donor Risk Rating'] == 'DONOR_AT_RISK', 'Donor Risk Rating'] ='At Risk'
risk_df.loc[risk_df['Donor Risk Rating'] == 'DONOR_INACTIVE', 'Donor Risk Rating'] ='Inactive'

risk_explaination_str = ''' 
    
    The "Donor Risk Report" shows what donors may be "falling off" based on their normal giving patters.

    All donors in this report have made at least one donation in the last rolling year.

    Using the average number of days between each donation and the number of days since their most recent donation, this report rates each donors risk of inactivity.

    If a donor has made a donation within two times their average number of days between a donation, they are considered "safe".

    If a donor has not made a donation within two times their average number of days between a donation but less than three times, they are considered in "warning".

    If a donor has not made a donation within three times their average number of days between a donation but less than four times, they are considered at "risk".

    If a donor has not made a donation within four times their average number of days between a donation or have only donated once outside of the last three months, they are considered "inactive".

                            '''

    
with st.expander("Click to Learn More"):
    st.write(risk_explaination_str)

st.subheader('Risk Reports')


safe_tab, warning_tab, risk_tab, inactive_tab, all_tab = st.tabs(['Safe Donors', 'Donors in Warning', 'Donors at Risk', 'Inactive Donors', 'All Donors'])

with safe_tab:
    st.dataframe(risk_df[risk_df['Donor Risk Rating'] == 'Safe'], use_container_width=True)
with warning_tab:
    st.dataframe(risk_df[risk_df['Donor Risk Rating'] == 'Warning'], use_container_width=True)
with risk_tab:
    st.dataframe(risk_df[risk_df['Donor Risk Rating'] == 'At Risk'], use_container_width=True)
with inactive_tab:
    st.dataframe(risk_df[risk_df['Donor Risk Rating'] == 'Inactive'], use_container_width=True)
with all_tab:
    st.dataframe(risk_df, use_container_width=True)
