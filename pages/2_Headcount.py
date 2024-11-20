# import packages

#from streamlit_dynamic_filters import DynamicFilters

explaination_str =  ''' The "Headcount Analytics Report" is a simple trend analysis of headcounts over time.

Before getting started, select an Event Name to review the headcounts of interest.

Below the line chart, there is a table breakdown of the trend to understand headcounts by all available features.

                '''

import streamlit as st
import pandas as pd
from datetime import timedelta

# Set page config
st.title('Headcount Analytics')

conn = st.connection('snowflake')

with st.expander("Click to Learn More"):
        st.write(explaination_str)


# load analytical dataframe
headcount_df = conn.query('''
    SELECT 
    STARTS_AT as "Starts At",
    ATTENDANCE_TYPE as "Attendance Type",
    DAY_NAME as "Day Name",
    EVENT_NAME as "Event Name",
    EVENT_TIME as "Event Time",
    FREQUENCY as "Frequency",
    GUEST_COUNT as "Guest Count",
    REGULAR_COUNT as "Regular Count",
    VOLUNTEER_COUNT as "Volunteer Count",
    TOTAL_ATTENDEES as "Total Attendees",
    Year(TRY_TO_Date(STARTS_AT)) as "Year" , 
    Week(TRY_TO_Date(STARTS_AT)) as "Week" 
    FROM ANALYTICAL_CHECKINS''', ttl=0)

headcount_df['Starts At'] = pd.to_datetime(headcount_df['Starts At']).dt.strftime("%Y-%m-%d")

headcount_df['Starts At'] = pd.to_datetime(headcount_df['Starts At'])

headcount_df['Date'] = pd.to_datetime(headcount_df['Starts At'])

headcount_df['Event Time'] = headcount_df['Event Time'].astype(str)

headcount_df['Year'] = headcount_df['Year'].astype(str)


headcount_df['Total Attendees'] = pd.to_numeric(headcount_df['Total Attendees'])
headcount_df['Regular Count'] = pd.to_numeric(headcount_df['Regular Count'])
headcount_df['Guest Count'] = pd.to_numeric(headcount_df['Guest Count'])
headcount_df['Volunteer Count'] = pd.to_numeric(headcount_df['Volunteer Count'])

 # get filters
col1, col2, col5, col6 = st.columns(4)


with col1:
    sel1 = st.multiselect(
            "Select Event Name",
            pd.Series(pd.unique(headcount_df['Event Name'])).sort_values(),
            pd.Series(pd.unique(headcount_df['Event Name'])).head(1),)
with col2:
    sel2 = st.multiselect(
            "Select Attendance Type",
            pd.Series(pd.unique(headcount_df['Attendance Type'])).sort_values(),
            pd.Series(pd.unique(headcount_df['Attendance Type'])).sort_values(),)
with col5:
    sel5 = st.date_input(
        "Select Start Event Date Range",
        value = headcount_df['Starts At'].max() - timedelta(days=365*2))
with col6:
    sel6 = st.date_input(
        "Select End Event Date Range",
        value = headcount_df['Starts At'].max())






df_selection = headcount_df.query('`Event Name`== @sel1').query('`Attendance Type`== @sel2').query('`Starts At`>= @sel5').query('`Starts At`<= @sel6')


trend_tab, yoy_tab = st.tabs(['Trend View', 'Year/Year View'])

with trend_tab:

    total_report, reg_report, guest_report, vol_report = st.tabs(['Total Headcount Report', 'Regular Headcount Report', 'Guest Headcount Report', 'Volunteer Headcount Report'])
    
    with total_report:
    
        if len(sel1) > 1:
    
            col_trend, col_event, col_time = st.columns(3)
            
            try:
                st.subheader('Total Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['Date'])['Total Attendees'].sum().reset_index(),
                    x="Date",
                    y="Total Attendees")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
            
            try:
                st.subheader('Total Headcount By Event')
                event_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Name'])['Total Attendees'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Total Attendees",
                    color='Event Name')
            except:
                col_event.write("No data for current selection. Try selecting more data.")
        
            try:
                st.subheader('Total Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Time'])['Total Attendees'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Total Attendees",
                    color='Event Time')
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
        else:
    
            col_trend, col_time = st.columns(2)
            
            try:
                st.subheader('Total Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['Date'])['Total Attendees'].sum().reset_index(),
                    x="Date",
                    y="Total Attendees")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
        
            try:
                st.subheader('Total Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Time'])['Total Attendees'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Total Attendees",
                    color='Event Time')
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
    with reg_report:
    
        if len(sel1) > 1:
    
            col_trend, col_event, col_time = st.columns(3)
            
            try:
                st.subheader('Regular Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['Date'])['Regular Count'].sum().reset_index(),
                    x="Date",
                    y="Regular Count")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
            
            try:
                st.subheader('Regular Headcount By Event')
                event_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Name'])['Regular Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Regular Count",
                    color='Event Name')
            except:
                col_event.write("No data for current selection. Try selecting more data.")
        
            try:
                st.subheader('Regular Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Time'])['Regular Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Regular Count",
                    color='Event Time')
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
        else:
    
            col_trend, col_time = st.columns(2)
            
            try:
                st.subheader('Regular Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['Date'])['Regular Count'].sum().reset_index(),
                    x="Date",
                    y="Regular Count")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
        
            try:
                st.subheader('Regular Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Time'])['Regular Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Regular Count",
                    color='Event Time')
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
    with guest_report:
    
        if len(sel1) > 1:
    
            col_trend, col_event, col_time = st.columns(3)
            
            try:
                st.subheader('Guest Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['Date'])['Guest Count'].sum().reset_index(),
                    x="Date",
                    y="Guest Count",)
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
            
            try:
                st.subheader('Guest Headcount By Event')
                event_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Name'])['Guest Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Guest Count",
                    color='Event Name')
            except:
                col_event.write("No data for current selection. Try selecting more data.")
        
            try:
                st.subheader('Guest Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Time'])['Guest Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Guest Count",
                    color='Event Time',)
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
        else:
    
            col_trend, col_time = st.columns(2)
    
            try:
                st.subheader('Guest Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['Date'])['Guest Count'].sum().reset_index(),
                    x="Date",
                    y="Guest Count",)
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
        
            try:
                st.subheader('Guest Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Time'])['Guest Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Guest Count",
                    color='Event Time',)
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
    with vol_report:
    
        if len(sel1) > 1:
    
            col_trend, col_event, col_time = st.columns(3)
            
            try:
                st.subheader('Volunteer Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['Date'])['Volunteer Count'].sum().reset_index(),
                    x="Date",
                    y="Volunteer Count")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
            
            try:
                st.subheader('Volunteer Headcount By Event')
                event_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Name'])['Volunteer Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Volunteer Count",
                    color='Event Name')
            except:
                col_event.write("No data for current selection. Try selecting more data.")
        
            try:
                st.subheader('Volunteer Headcount Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Time'])['Volunteer Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Volunteer Count",
                    color='Event Time',)
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
        else:
    
            col_trend, col_time = st.columns(2)
            
            try:
                st.subheader('Volunteer Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['Date'])['Volunteer Count'].sum().reset_index(),
                    x="Date",
                    y="Volunteer Count",)
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
        
            try:
                st.subheader('Volunteer Headcount Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['Date', 'Event Time'])['Volunteer Count'].sum().reset_index(),
                    #df_selection,
                    x="Date",
                    y="Volunteer Count",
                    color='Event Time',)
            except:
                col_time.write("No data for current selection. Try selecting more data.")



with yoy_tab:

    st.subheader('Total Headcount Year/Year')
    st.bar_chart(
        df_selection.groupby(['Year', 'Week'])['Total Attendees'].sum().reset_index(),
        x="Week", y="Total Attendees", color='Year')

    st.subheader('Regular Headcount Year/Year')
    st.bar_chart(
        df_selection.groupby(['Year', 'Week'])['Regular Count'].sum().reset_index(),
        x="Week", y="Regular Count", color='Year')

    st.subheader('Guest Headcount Year/Year')
    st.bar_chart(
        df_selection.groupby(['Year', 'Week'])['Guest Count'].sum().reset_index(),
        x="Week", y="Guest Count", color='Year')

    st.subheader('Volunteer Headcount Year/Year')
    st.bar_chart(
        df_selection.groupby(['Year', 'Week'])['Volunteer Count'].sum().reset_index(),
        x="Week", y="Volunteer Count", color='Year')


st.subheader('Table View')
df_selection['Starts At'] = df_selection['Starts At'].dt.strftime(date_format = '%Y-%m-%d')
st.write(df_selection.set_index('Starts At').drop(columns=['Year', 'Week', 'Date']))
