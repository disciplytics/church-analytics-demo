# import packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

activity_explaination_str = ''' The "Activity Report" shows activity trends for people in you church. Select different activities to compare and contrast.

Select the date range to query the year(s) you are intereseted. Either use the calendar tool or type in the dates!

The Activity Sequence visual uses the sequence your church has entered in your database.
'''

conn = st.connection('snowflake')

st.title('Activity Report')

with st.expander("Click to Learn More"):
        st.write(activity_explaination_str)

field_data = conn.query('''
SELECT
    PRIMARY_CAMPUS as "Primary Campus",
    AGE_GROUP as "Age Group",
    MEMBERSHIP as "Membership",
    MARITAL_STATUS as "Marital Status",
    ACTIVITY_DATE as "Activity Date",
    YEAR(CAST(ACTIVITY_DATE as DATE)) as "Year",
    ACTIVITY as "Activity",
    ACTIVITY_SEQUENCE as "Sequence",
    ACTIVITY_TYPE as "Activity Type",
    PERSON_ID
    
FROM ANALYTICAL_FIELD''', ttl=0)

field_data['Year'] = field_data['Year'].astype(str)

col11, col12, col13, col14 = st.columns(4)

with col11:
    sel11 = st.multiselect(
            "Select Primary Campus",
            field_data['Primary Campus'].unique(),
            default = field_data['Primary Campus'].unique())
with col12:
    sel12 = st.multiselect(
            "Select Age Group",
            field_data['Age Group'].unique(),
            default = field_data['Age Group'].unique())
with col13:
    sel13 = st.multiselect(
            "Select Membership",
            field_data['Membership'].unique(),
            default = field_data['Membership'].unique())
with col14:
    sel14 = st.multiselect(
            "Select Marital Status",
            field_data['Marital Status'].unique(),
            default = field_data['Marital Status'].unique())

people_act_data = field_data.query('`Primary Campus`== @sel11').query('`Age Group`== @sel12').query('`Membership`== @sel13').query('`Marital Status`== @sel14')
people_act_data['Activity Date'] = pd.to_datetime(people_act_data['Activity Date'])

sel15 = st.multiselect(
        "Select Activity Type",
        people_act_data['Activity Type'].unique(),
        default = people_act_data['Activity Type'].unique())

people_act_data = people_act_data.query('`Activity Type`== @sel15')

sel5 = st.multiselect(
        "Select Activity (More In Drop Down!)",
        people_act_data['Activity'].unique(),
        default = people_act_data['Activity'].unique()[:5])

col20, col21 = st.columns(2)

with col20:
    sel20 = st.date_input(
        "Select Start Activity Date Range",
        value = pd.to_datetime(people_act_data['Activity Date'].min()))
with col21:
    sel21 = st.date_input(
        "Select End Activity Date Range",
        value = pd.to_datetime(people_act_data['Activity Date'].max()))

people_act_data = people_act_data.query('`Activity`== @sel5').query('`Activity Date`>= @sel20').query('`Activity Date`<= @sel21')

people_act_data['Sequence'] = people_act_data['Sequence'].astype(str)
people_act_data['count'] = np.random.randint(1, 3, people_act_data.shape[0])


st.altair_chart(
    alt.Chart(people_act_data, 
              title = 'Activity Trends').mark_bar().encode(
            color = 'Year',
            x=alt.X('Activity Date'), 
            y=alt.Y('sum(count)').title('Total People')), 
        use_container_width=True)

st.altair_chart(
    alt.Chart(people_act_data, 
              title = 'Activity Sequence').mark_bar().encode(
            color = 'Activity',
            x=alt.X('Sequence'), 
            y=alt.Y('count(PERSON_ID)').title('Total People')), 
        use_container_width=True)

st.subheader('Activity Breakdowns')

col_act1, col_act2 = st.columns(2)


col_act1.altair_chart(
    alt.Chart(people_act_data, 
              title = 'Activity By Primary Campus').mark_bar().encode(
            color = 'Primary Campus',
            y=alt.Y('Activity').title(""), 
            x=alt.X('count(PERSON_ID)').title('Total People')), 
        use_container_width=True)

col_act2.altair_chart(
    alt.Chart(people_act_data, 
              title = 'Activity By Membership').mark_bar().encode(
            color = 'Membership',
            y=alt.Y('Activity').title(""), 
            x=alt.X('count(PERSON_ID)').title('Total People')), 
        use_container_width=True)

col_act3, col_act4 = st.columns(2)


col_act3.altair_chart(
    alt.Chart(people_act_data, 
              title = 'Activity By Age Group').mark_bar().encode(
            color = 'Age Group',
            y=alt.Y('Activity').title(""), 
            x=alt.X('count(PERSON_ID)').title('Total People')), 
        use_container_width=True)

col_act4.altair_chart(
    alt.Chart(people_act_data, 
              title = 'Activity By Marital Status').mark_bar().encode(
            color = 'Marital Status',
            y=alt.Y('Activity').title(""), 
            x=alt.X('count(PERSON_ID)').title('Total People')), 
        use_container_width=True)
