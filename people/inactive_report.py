# import packages
]import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

inactive_explaination_str = ''' The "Inactive Report" shows what types of people have been inactive and why they went inactive.'''


conn = st.connection('snowflake')

st.title('Inactive Report')

with st.expander("Click to Learn More"):
    st.write(inactive_explaination_str)    

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

inactive_data = people_data[(people_data['Status'] == 'inactive')]


col6, col7, col8, col9 = st.columns(4)

with col6:
    sel6 = st.multiselect(
            "Primary Campus",
            inactive_data['Primary Campus'].unique(),
            default = inactive_data['Primary Campus'].unique())
with col7:
    sel7= st.multiselect(
            "Age Group",
            inactive_data['Age Group'].unique(),
            default = inactive_data['Age Group'].unique())
with col8:
    sel8 = st.multiselect(
            "Membership",
            inactive_data['Membership'].unique(),
            default = inactive_data['Membership'].unique())
with col9:
    sel9 = st.multiselect(
            "Marital Status",
            inactive_data['Marital Status'].unique(),
            default = inactive_data['Marital Status'].unique())


    

inactive_selection = inactive_data.query('`Primary Campus`== @sel6').query('`Age Group`== @sel7').query('`Membership`== @sel8').query('`Marital Status`== @sel9')

st.subheader('Inactived People Trends')

st.altair_chart(
        alt.Chart(inactive_selection).transform_window(
        Total='count(Status)',
        sort=[{"field": "Inactivated At"}],
        #groupby=['Year'],
    ).mark_line().encode(
        x='Inactivated At:T',
        y='Total:Q',
       # color='Year:N',
    ),
        use_container_width=True
    )

st.subheader('Inactive Reasons')
st.altair_chart(
            alt.Chart(inactive_selection, title = 'Total Inactive People By Inactive Reason').mark_bar().encode(
                    y=alt.Y('Inactive Reason').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)

st.subheader('Inactive People Breakdowns')
col1i, col2i = st.columns(2)
col1i.altair_chart(
            alt.Chart(inactive_selection, title = 'Total Inactive People By Membership').mark_bar().encode(
                    y=alt.Y('Membership').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)
col2i.altair_chart(
            alt.Chart(inactive_selection, title = 'Total Inactive People By Marital Status').mark_bar().encode(
                    y=alt.Y('Marital Status').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)
    
col3i, col4i = st.columns(2)
col3i.altair_chart(
            alt.Chart(inactive_selection, title = 'Total Inactive People By Age Group').mark_bar().encode(
                    y=alt.Y('Age Group').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)
col4i.altair_chart(
            alt.Chart(inactive_selection, title = 'Total Inactive People By Primary Campus').mark_bar().encode(
                    y=alt.Y('Primary Campus').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)
