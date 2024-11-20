# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

#from streamlit_dynamic_filters import DynamicFilters

explaination_str = ''' The Group Analytics report displays attendance rate trends and group member demographics and locations.

Select one group at a time for optimal performance.


                '''


# Get current session
conn = st.connections('snowflake')

# Set page config
st.title('Group Analytics')

with st.expander("Click to Learn More"):
        st.write(explaination_str)


# load analytical dataframe
group_df = conn.query('''
    select 
        *, 
        year(CAST(STARTS_AT as DATE)) as "Year", 
        week(CAST(STARTS_AT as DATE)) as "Week"
        FROM ANALYTICAL_GROUPS_ATTENDANCE''', ttl=0)




group_df.rename(columns={
    'ATTENDANCE_ID':'Attendance ID',
    'ATTENDED': 'Attended',
    'ROLE': 'Role',
    'MEMBERSHIP': 'Membership',
    #'STATUS'
    'PRIMARY_CAMPUS': 'Primary Campus',
    'MARITAL_STATUS': 'Marital Status',
    'PERSON_LATITUDE': 'Person Latitude',
    'PERSON_LONGITUDE': 'Person Longitude',
    'AGE_GROUP': 'Age Group',
    #'TENURE'
    #'MARRIAGE_LENGTH'
    #'AGE'
    'STARTS_AT': 'Starts At',
    'ENDS_AT': 'Ends At',
    #'MULTI_DAY'
    #'REPEATING'
    'GROUP_NAME': 'Group Name',
    #'SCHEDULE'
    'LOCATION_NAME': 'Location Name',
    'GROUP_LATITUDE': 'Group Latitude',
    'GROUP_LONGITUDE': 'Group Longitutde',
    'MILES_BETWEEN_GROUP_PERSON': 'Distance Traveled By Attendee (Miles)'
}, inplace=True)


## Calc metrics

# round miles
group_df['Distance Traveled By Attendee (Miles)'] = np.round(pd.to_numeric(group_df['Distance Traveled By Attendee (Miles)']),2)

# convert lat and long
group_df['Person Latitude'] = pd.to_numeric(group_df['Person Latitude'])
group_df['Person Longitude'] = pd.to_numeric(group_df['Person Longitude'])

# calc attendances
group_df.loc[group_df['Attended'] == 'True', 'Attendances'] = 1
group_df['Attendances'] = group_df['Attendances'].fillna(0)

# calc attendance rate
group_df.loc[group_df['Attended'] == 'True', 'Attended'] = 1
group_df.loc[group_df['Attended'] == 'False', 'Attended'] = 0

group_df['Year'] = group_df['Year'].astype(str)

dates = ['Starts At', 'Ends At']
for i in dates:
    group_df[i] = pd.to_datetime(group_df[i])

 # get filters
col1, col2, col3, col4 = st.columns(4)


with col1:
    sel1 = st.multiselect(
            "Select Group Name (Click to see more!)",
            pd.Series(pd.unique(group_df['Group Name'])).sort_values(),
            pd.Series(pd.unique(group_df['Group Name'])).sort_values()[:1]
            )
with col2:
    sel2 = st.multiselect(
            "Select Primary Campus",
            pd.Series(pd.unique(group_df['Primary Campus'])).sort_values(),
            pd.Series(pd.unique(group_df['Primary Campus'])).sort_values())

with col3:
    sel3 = st.date_input(
        "Select Start Group Date Range",
        value = pd.to_datetime(group_df['Starts At'].min()))
with col4:
    sel4 = st.date_input(
        "Select End Group Date Range",
        value = pd.to_datetime(group_df['Ends At'].max()))


#group_df['STARTS_AT'] = pd.to_datetime(group_df['STARTS_AT']).dt.strftime("%Y-%m-%d")
#group_df['ENDS_AT'] = pd.to_datetime(group_df['ENDS_AT']).dt.strftime("%Y-%m-%d")

df_selection = group_df.query('`Group Name`== @sel1').query('`Primary Campus`== @sel2').query('`Starts At`>= @sel3').query('`Ends At`<= @sel4')



st.subheader('Attendance Rate Year Over Year')
st.altair_chart(
        alt.Chart(df_selection).mark_line().encode(
                color='Year',
                x=alt.X('Week', 
                        axis=alt.Axis(tickMinStep=1),
                        scale=alt.Scale(domain=[1, 53])), 
                y=alt.Y('mean(Attended)').axis(format='%').title('Attendance Rate')), 
            use_container_width=True)

st.subheader('Attendance Rate Breakdowns')
col1, col2 = st.columns(2)
col1.altair_chart(
        alt.Chart(df_selection, title = 'Attendance Rate By Membership').mark_bar().encode(
                y=alt.Y('Membership'), 
                x=alt.X('mean(Attended)').axis(format='%').title('Attendance Rate')), 
            use_container_width=True)
col2.altair_chart(
        alt.Chart(df_selection, title = 'Attendance Rate By Marital Status').mark_bar().encode(
                y=alt.Y('Marital Status'), 
                x=alt.X('mean(Attended)').axis(format='%').title('Attendance Rate')), 
            use_container_width=True)

col3, col4 = st.columns(2)
col3.altair_chart(
        alt.Chart(df_selection, title = 'Attendance Rate By Age Group').mark_bar().encode(
                y=alt.Y('Age Group'), 
                x=alt.X('mean(Attended)').axis(format='%').title('Attendance Rate')), 
            use_container_width=True)
col4.altair_chart(
        alt.Chart(df_selection, title = 'Attendance Rate By Location Name').mark_bar().encode(
                y=alt.Y('Location Name'), 
                x=alt.X('mean(Attended)').axis(format='%').title('Attendance Rate')), 
            use_container_width=True)


st.altair_chart(
        alt.Chart(df_selection, title = 'Attendance Rate By Distance Traveled to Group').mark_point().encode(
                x=alt.X('Distance Traveled By Attendee (Miles)'), 
                y=alt.Y('mean(Attended)').axis(format='%').title('Attendance Rate')), 
            use_container_width=True)
