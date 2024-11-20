# import packages
# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


people_explaination_str = ''' The People Report breaks down the who, what, and where of the people in your database.'''

conn = st.connection('snowflake')

st.title('People Report')


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

people_data['LONGITUDE'] = np.round(pd.to_numeric(people_data['LONGITUDE'], errors='coerce'),2)
people_data['LATITUDE'] = np.round(pd.to_numeric(people_data['LATITUDE'], errors='coerce'),2)
#people_data['Created At'] = pd.to_datetime(people_data['Created At'], format = '%Y-%m-%d')

with st.expander("Click to Learn More"):
  st.write(adult_explaination_str)    

col1, col2, col3, col4 = st.columns(4)

with col1:
    sel1 = st.multiselect(
            "Select Primary Campus",
            people_data['Primary Campus'].unique(),
            default = people_data['Primary Campus'].unique())
with col2:
    sel2 = st.multiselect(
            "Select Age Group",
            people_data['Age Group'].unique(),
            default = people_data['Age Group'].unique())
with col3:
    sel3 = st.multiselect(
            "Select Membership",
            people_data['Membership'].unique(),
            default = people_data['Membership'].unique())
with col4:
    sel4 = st.multiselect(
            "Select Active Status",
            people_data['Status'].unique(),
            default = 'active')


    
people_selection = people_data.query('`Primary Campus`== @sel1').query('`Age Group`== @sel2').query('`Membership`== @sel3').query('`Status`== @sel4')


tab1, tab2 = st.tabs(['Overview', 'People Location Map'])

with tab1:
    st.subheader('Newly Created People Trends')

    st.altair_chart(
        alt.Chart(people_selection).transform_window(
        Total='count(Status)',
        sort=[{"field": "Created At"}],
        #groupby=['Year'],
    ).mark_line().encode(
        x='Created At:T',
        y='Total:Q',
       # color='Year:N',
    ),
        use_container_width=True
    )

    st.subheader('People Breakdowns')
    col1, col2 = st.columns(2)
    col1.altair_chart(
            alt.Chart(people_selection, title = 'Total People By Membership').mark_bar().encode(
                    y=alt.Y('Membership').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)
    col2.altair_chart(
            alt.Chart(people_selection, title = 'Total People By Marital Status').mark_bar().encode(
                    y=alt.Y('Marital Status').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)
    
    col3, col4 = st.columns(2)
    col3.altair_chart(
            alt.Chart(people_selection, title = 'Total People By Age Group').mark_bar().encode(
                    y=alt.Y('Age Group').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)
    col4.altair_chart(
            alt.Chart(people_selection, title = 'Total People By Primary Campus').mark_bar().encode(
                    y=alt.Y('Primary Campus').title(""), 
                    x=alt.X('count(PERSON_ID)').title('Total People')), 
                use_container_width=True)
    

with tab2:
    col_map, col_tab_map = st.columns(2)
    col_map.subheader('People Locations')
    def show():
        return col_map.map(people_selection.groupby(['LATITUDE', 'LONGITUDE'])['PERSON_ID'].size().reset_index(), size='PERSON_ID', use_container_width=True)
    show()

    col_tab_map.subheader('People Location Breakdown')
    col_tab_map.write(
        people_selection.groupby(['Location'])[['PERSON_ID', 'HOUSEHOLD_ID']].nunique().sort_values(by=['PERSON_ID'], ascending=False).rename(columns={'PERSON_ID':'Number of People', 'HOUSEHOLD_ID': 'Number of Households'})
    )
