# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# connect to snowflake
conn = st.connection("snowflake")

# Page Parameters
st.header("Year/Year Giving Report")

# GET FILTERS
filter_years = conn.query('''
    SELECT
        DISTINCT DONATION_YEAR as YEAR,
    FROM ANALYTICS.ANALYTICAL_GIVING

''', ttl=0)

filter_pcs = conn.query('''
    SELECT
        DISTINCT PRIMARY_CAMPUS as PRIMARY_CAMPUS,
    FROM ANALYTICS.ANALYTICAL_GIVING

''', ttl=0)


        
## YOY REPORT
filter_year_col, filter_pc_col, fill1, fill2 = st.columns([.25, .25, .25, .25])
with filter_year_col:
    giving_year_sel = st.multiselect(
            'Select Years to Compare',
            options = filter_years['YEAR'],
            default = [filter_years['YEAR'].max(), filter_years['YEAR'].max()-1],
        )

with filter_pc_col:
    giving_pc_sel = st.multiselect(
                'Select Primary Campus',
                options = filter_pcs['PRIMARY_CAMPUS'],
                default = filter_pcs['PRIMARY_CAMPUS'],
            )
yoy_df = conn.query('''
    SELECT 
    CAST(DONATION_YEAR as INT) as "Year",
    CAST(DONATION_MONTH as INT) as "Month",
    CAST(DONATION_WEEK as INT) as "Week",
    CAST(RECEIVED_AT as DATE) as "Date",
    PRIMARY_CAMPUS as "Primary Campus",
    FUND_NAME as "Fund",
    MEMBERSHIP as "Membership",
  CONCAT(CITY,', ',STATE,' ',ZIP) as "Location",
  CAST(LATITUDE as FLOAT) as "Latitude",
  CAST(LONGITUDE as FLOAT) as "Longitude",
    SUM(DONATION_AMOUNT) as "Donations",
    PERSON_ID as "Donors",
    HOUSEHOLD_PERSON_ID as "Donor Households"
FROM ANALYTICS.ANALYTICAL_GIVING
GROUP BY ALL    
''', ttl=0)

# set default and options, have plan in case church only has one year
try:
    default_giving_years = [yoy_df['Year'].max(), yoy_df['Year'].max() - 1]
    option_giving_years = yoy_df['Year'].unique()

    max_year_week = yoy_df[yoy_df['Year'] == yoy_df['Year'].max()]['Week'].max()
    max_year = yoy_df['Year'].max()
    
except:
    default_giving_years = [yoy_df['Year'].max(),]
    option_giving_years = yoy_df['Year'].unique()

    max_year_week = 52
    max_year = yoy_df['Year'].max()


yoy_df_sel = yoy_df.query('`Year`==@giving_year_sel')

yoy_df_sel = yoy_df_sel.query('`Primary Campus`==@giving_pc_sel')

# data is filtered by user and can be used for analysis
#######################################################

try:
    # calculate metrics
    most_recent_yr = int(pd.Series(giving_year_sel).max())
    least_recent_yr = int(pd.Series(giving_year_sel).min())
    label_val_ytd = f"YTD Giving - {most_recent_yr}"

    most_recent_ytd = yoy_df_sel[yoy_df_sel['Year'] == most_recent_yr]['Donations'].sum()
    most_recent_avg = yoy_df_sel[yoy_df_sel['Year'] == most_recent_yr]['Donations'].mean()

    label_val_yoy = f"Y/Y Giving - {most_recent_yr}"

    label_val_avg = f"Average Gift - {most_recent_yr}"

    # create reporting params for max year selected
    if most_recent_yr != int(max_year):
        delta_ytd = yoy_df_sel[yoy_df_sel['Year'] == least_recent_yr]['Donations'].sum()

        delta_avg = yoy_df_sel[yoy_df_sel['Year'] == least_recent_yr]['Donations'].mean()
    else:   
        delta_ytd = yoy_df_sel[(yoy_df_sel['Year'] == least_recent_yr) &
                                  (yoy_df_sel['Week'] <= max_year_week)]['Donations'].sum()

        delta_avg = yoy_df_sel[(yoy_df_sel['Year'] == least_recent_yr) &
                                  (yoy_df_sel['Week'] <= max_year_week)]['Donations'].mean()

    # metrics
    ytd_col, yoy_col, avg_col = st.columns(3)
    
    ytd_col.metric(
        label=label_val_ytd,
        value= '${:,}'.format(np.round(most_recent_ytd,2)),
        delta = f"YTD - {least_recent_yr}: {'${:,}'.format(np.round(delta_ytd/1000,2))}K",
        delta_color="off"
    )

    yoy_col.metric(
        label=f'{label_val_yoy}/{least_recent_yr}',
        value= f"{np.round((most_recent_ytd - delta_ytd)/ delta_ytd * 100,2)}%",
    )

    avg_col.metric(
        label=label_val_avg,
        value= '${:,}'.format(np.round(most_recent_avg,2)),
        delta = f"Avg Gift - {least_recent_yr}: {'${:,}'.format(np.round(delta_avg,2))}",
        delta_color="off"
    )

    # time series analysis
    # add yoy tabs
    yoy_df_sel['Year'] = yoy_df_sel['Year'].astype(str)
    yoy_df['Year'] = yoy_df['Year'].astype(str)
    st.subheader('Giving Trends')
    yoy_w_tab, yoy_m_tab, trend_tab = st.tabs(['Year/Year By Week', 'Year/Year By Month', 'Giving Trend'])
    
    with yoy_w_tab:
        st.altair_chart(alt.Chart(yoy_df_sel).mark_bar().encode(
            x=alt.X('Week', axis=alt.Axis(tickMinStep=1),scale=alt.Scale(domain=[1, 53])), y='sum(Donations)',color='Year'), use_container_width=True)
    with yoy_m_tab:
        st.altair_chart(alt.Chart(yoy_df_sel).mark_bar().encode(
            x=alt.X('Month', axis=alt.Axis(tickCount=12),scale=alt.Scale(domain=[1, 12])), y='sum(Donations)',color='Year'), use_container_width=True)
    with trend_tab:
        st.altair_chart(alt.Chart(yoy_df).mark_line().encode(
            x='Year', y='sum(Donations)',color='Primary Campus'), use_container_width=True)

            
    # Create the breakdown analysis
    ###############################
    st.subheader("Giving Breakdowns")
    pc_toggle = st.toggle('Include Primary Campus In Breakdown')
    member_tab, location_tab, fund_tab = st.tabs(['Giving By Membership', 'Giving By Location', 'Giving By Fund'])

    with member_tab:               
        if pc_toggle:
            
            mem_df = yoy_df_sel.groupby(['Primary Campus', 'Membership', 'Year'])[['Donations', 'Donors']].agg({'Donations':'sum','Donors':'nunique'}).reset_index()
            st.altair_chart(
                alt.hconcat(
                alt.Chart(mem_df).mark_bar().encode(
                    alt.X('sum(Donations):Q'),
                    alt.Y('Membership:O'),
                    color='Year:N',
                    row='Primary Campus:N'
                ),
                alt.Chart(mem_df).mark_bar().encode(
                    alt.X('sum(Donors):Q'),
                    alt.Y('Membership:O').title(None),
                    color='Year:N',
                    row=alt.Row('Primary Campus:N').title(None)
                ))
                , use_container_width=True)
        else:
            mem_df = yoy_df_sel.groupby(['Membership','Year'])[['Donations', 'Donors']].agg({'Donations':'sum','Donors':'nunique'}).reset_index()
            st.altair_chart(
                alt.hconcat(
                alt.Chart(mem_df).mark_bar().encode(
                    alt.X('sum(Donations):Q'),
                    alt.Y('Membership:O'),
                    color='Year:N',
                ),
                alt.Chart(mem_df).mark_bar().encode(
                    alt.X('sum(Donors):Q'),
                    alt.Y('Membership:O').title(None),
                    color='Year:N',
                ))
                , use_container_width=True)

    with location_tab:
        if pc_toggle:
            
            loc_df = yoy_df_sel.groupby(['Primary Campus', 'Location', 'Year'])[['Donations', 'Donors']].agg({'Donations':'sum','Donors':'nunique'}).reset_index()
            st.altair_chart(
                alt.hconcat(
                alt.Chart(loc_df).mark_bar().encode(
                    alt.X('sum(Donations):Q'),
                    alt.Y('Location:O'),
                    color='Year:N',
                    row='Primary Campus:N'
                ),
                alt.Chart(loc_df).mark_bar().encode(
                    alt.X('sum(Donors):Q'),
                    alt.Y('Location:O').title(None),
                    color='Year:N',
                    row=alt.Row('Primary Campus:N').title(None),
                ))
                , use_container_width=True)
        else:
            loc_df = yoy_df_sel.groupby(['Location','Year'])[['Donations', 'Donors']].agg({'Donations':'sum','Donors':'nunique'}).reset_index()
            st.altair_chart(
                alt.hconcat(
                alt.Chart(loc_df).mark_bar().encode(
                    alt.X('sum(Donations):Q'),
                    alt.Y('Location:O'),
                    color='Year:N',
                ),
                alt.Chart(loc_df).mark_bar().encode(
                    alt.X('sum(Donors):Q'),
                    alt.Y('Location:O').title(None),
                    color='Year:N',
                ))
                , use_container_width=True)

    with fund_tab:
        if pc_toggle:
            
            fund_df = yoy_df_sel.groupby(['Primary Campus', 'Fund', 'Year'])[['Donations', 'Donors']].agg({'Donations':'sum','Donors':'nunique'}).reset_index()
            st.altair_chart(
                alt.hconcat(
                alt.Chart(fund_df).mark_bar().encode(
                    alt.X('sum(Donations):Q'),
                    alt.Y('Fund:O'),
                    color='Year:N',
                    row='Primary Campus:N'
                ),
                alt.Chart(fund_df).mark_bar().encode(
                    alt.X('sum(Donors):Q'),
                    alt.Y('Fund:O').title(None),
                    color='Year:N',
                    row=alt.Row('Primary Campus:N').title(None)
                ))
                , use_container_width=True)
        else:
            fund_df = yoy_df_sel.groupby(['Fund','Year'])[['Donations', 'Donors']].agg({'Donations':'sum','Donors':'nunique'}).reset_index()
            st.altair_chart(
                alt.hconcat(
                alt.Chart(fund_df).mark_bar().encode(
                    alt.X('sum(Donations):Q'),
                    alt.Y('Fund:O'),
                    color='Year:N',
                ),
                alt.Chart(fund_df).mark_bar().encode(
                    alt.X('sum(Donors):Q'),
                    alt.Y('Fund:O').title(None),
                    color='Year:N',
                ))
                , use_container_width=True)
    
except:
    st.write('Select More Data.')
