# import packages
# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

conn = st.connection('snowflake')
#from streamlit_dynamic_filters import DynamicFilters

adult_explaination_str = ''' The People Report breaks down the who, what, and where of the people in your database.'''
activity_explaination_str = ''' The "Activity Report" shows activity trends for people in you church. Select different activities to compare and contrast.

Select the date range to query the year(s) you are intereseted. Either use the calendar tool or type in the dates!

The Activity Sequence visual uses the sequence your church has entered in your database.
'''


inactive_explaination_str = ''' The "Inactive Report" shows what types of people have been inactive and why they went inactive.'''
pdq_explaination_str = ''' The "People Data Quality Report" gives three tables of key data points. 

Years Since Last Update: List of active person ids sorted by how many years has passed since the person record has been updated.

Missing Primay Campus: List of active person ids who are not assigned to a campus.

Missing Birthdate: List of active person ids who do not have a recorded birthdate.
'''







# Set page config
st.title('People Analytics')




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

people_tab, activity_tab, inactive_report, quality_tab = st.tabs(["People Report", "Activity Report", "Inactive Report", "People Data Quality Report"])

#people tab
with people_tab:
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
with activity_tab:
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
                "Primary Campus",
                field_data['Primary Campus'].unique(),
                default = field_data['Primary Campus'].unique())
    with col12:
        sel12 = st.multiselect(
                "Age Group",
                field_data['Age Group'].unique(),
                default = field_data['Age Group'].unique())
    with col13:
        sel13 = st.multiselect(
                "Membership",
                field_data['Membership'].unique(),
                default = field_data['Membership'].unique())
    with col14:
        sel14 = st.multiselect(
                "Marital Status",
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


    st.altair_chart(
        alt.Chart(people_act_data, 
                  title = 'Activity Trends').mark_bar().encode(
                color = 'Year',
                x=alt.X('Activity Date'), 
                y=alt.Y('count(PERSON_ID)').title('Total People')), 
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


with inactive_report:
    with st.expander("Click to Learn More"):
        st.write(inactive_explaination_str)    

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

with quality_tab:
    with st.expander("Click to Learn More"):
        st.write(pdq_explaination_str)
        
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
