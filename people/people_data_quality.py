# import packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

pdq_explaination_str = ''' The "People Data Quality Report" gives three tables of key data points. 

Years Since Last Update: List of active person ids sorted by how many years has passed since the person record has been updated.

Missing Primay Campus: List of active person ids who are not assigned to a campus.

Missing Birthdate: List of active person ids who do not have a recorded birthdate.
'''

conn = st.connection('snowflake')

st.title('Data Quality Report')

with st.expander("Click to Learn More"):
    st.write(pdq_explaination_str)    

# load analytical dataframe
people_data = conn.query('''
SELECT 
    LONGITUDE,
    LATITUDE,
    PRIMARY_CAMPUS as "Primary Campus",
    AGE_GROUP as "Age Group",
    STATUS as "Status",
    MEMBERSHIP as "Membership",
    MARITAL_STATUS as "Marital Status",
    PERSON_ID,
    HOUSEHOLD_ID,
    AGE as "Age",
    YEARS_SINCE_UPDATE as "Years Since Update",
    INACTIVE_REASON as "Inactive Reason",
    CONCAT(CITY, ',' , STATE) as "Location",
    DATE_TRUNC('month', CREATED_AT) as "Created At",
    DATE_TRUNC('month', INACTIVATED_AT) as "Inactivated At",
    YEAR(CAST(CREATED_AT as DATE)) as "Year",
    WEEK(CAST(CREATED_AT as DATE)) as "Week"
FROM ANALYTICAL_PEOPLE''', ttl=0)
    
quality_selection = people_data[(people_data['Status'] == 'active')]

yrs_update_col, missing_campus_col, missing_birthdate_col = st.columns(3)

with yrs_update_col:
    st.subheader("Years Since Last Update")
    st.dataframe(quality_selection.sort_values(by=['Years Since Update'], ascending = False)[['PERSON_ID', 'Years Since Update']].reset_index(drop=True).rename(columns={'PERSON_ID':'Person ID'}).set_index('Person ID'),
                use_container_width = True)

with missing_campus_col:
    st.subheader("Missing Primary Campus")
    st.dataframe(quality_selection[quality_selection['Primary Campus'] == 'Unknown'].sort_values(by=['Years Since Update'], ascending = False)[['PERSON_ID', 'Primary Campus', 'Years Since Update']].reset_index(drop=True).rename(columns={'PERSON_ID':'Person ID'}).set_index('Person ID'),
                use_container_width = True)


with missing_birthdate_col:
    st.subheader("Missing Birthdate")
    st.dataframe(quality_selection[quality_selection['Age'].isna() == True].sort_values(by=['Years Since Update'], ascending = False).rename(columns={'Age':'Birthdate'})[['PERSON_ID', 'Birthdate', 'Years Since Update']].fillna('Unknown').reset_index(drop=True).rename(columns={'PERSON_ID':'Person ID'}).set_index('Person ID'),
                use_container_width = True)
