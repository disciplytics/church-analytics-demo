# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# connect to snowflake
conn = st.connection("snowflake")

# Page Parameters
st.set_page_config(page_title = "Giving Analytics", layout='wide')
st.header("Giving Analytics")
st.write("Multiple reports to better understand giving in your church.")
# Get the current credentials
session = get_active_session()

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


# tab parameters
yoy_tab, fee_tab, forecast_tab, risk_tab = st.tabs(['Year/Year Report', 'Fee Report', 'Giving Forecast Report', 'Donor Risk Report'])


        
## YOY REPORT
with yoy_tab:
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


## FEE REPORT
with fee_tab:

    filter_year_col2, filter_pc_col2, fill3, fill4 = st.columns([.25, .25, .25, .25])
    with filter_year_col2:
        giving_year_sel = st.multiselect(
                'Select Years To Compare',
                options = filter_years['YEAR'],
                default = [filter_years['YEAR'].max(), filter_years['YEAR'].max()-1],
            )
    
    with filter_pc_col2:
        giving_pc_sel = st.multiselect(
                    'Select a Primary Campus',
                    options = filter_pcs['PRIMARY_CAMPUS'],
                    default = filter_pcs['PRIMARY_CAMPUS'],
                )

    
    fee_df = conn.query('''
        SELECT 
        CAST(DONATION_YEAR as INT) as "Year",
        CAST(DONATION_MONTH as INT) as "Month",
        CAST(DONATION_WEEK as INT) as "Week",
        CAST(RECEIVED_AT as DATE) as "Date",
        PRIMARY_CAMPUS as "Primary Campus",
        PAYMENT_SOURCE as "Payment Source",
        PAYMENT_METHOD_SUB as "Payment Source Sub",
        PAYMENT_BRAND as "Payment Brand",
        SUM(FEE_AMOUNT) as "Fee Amount",
        AVG(FEE_PERCENTAGE) as "Fee Percentage"
    FROM ANALYTICS.ANALYTICAL_GIVING
    GROUP BY ALL    
    ''', ttl=0)

    # set default and options, have plan in case church only has one year
    try:
        default_giving_years = [fee_df['Year'].max(), fee_df['Year'].max() - 1]
        option_giving_years = fee_df['Year'].unique()
    
        max_year_week = fee_df[fee_df['Year'] == fee_df['Year'].max()]['Week'].max()
        max_year = fee_df['Year'].max()
        
    except:
        default_giving_years = [fee_df['Year'].max(),]
        option_giving_years = fee_df['Year'].unique()
    
        max_year_week = 52
        max_year = fee_df['Year'].max()



    fee_df_sel = fee_df.query('`Year`==@giving_year_sel')
    
    fee_df_sel = fee_df_sel.query('`Primary Campus`==@giving_pc_sel')

    # data is filtered by user and can be used for analysis
    #######################################################

    try:
        # calculate metrics
        most_recent_yr = int(pd.Series(giving_year_sel).max())
        least_recent_yr = int(pd.Series(giving_year_sel).min())
        label_val_ytd = f"YTD Fees - {most_recent_yr}"
    
        most_recent_ytd = fee_df_sel[fee_df_sel['Year'] == most_recent_yr]['Fee Amount'].sum()
        most_recent_avg = fee_df_sel[fee_df_sel['Year'] == most_recent_yr]['Fee Amount'].mean()
    
        label_val_yoy = f"Y/Y Fees - {most_recent_yr}"
    
        label_val_avg = f"Average Fee - {most_recent_yr}"
    
        # create reporting params for max year selected
        if most_recent_yr != int(max_year):
            delta_ytd = fee_df_sel[fee_df_sel['Year'] == least_recent_yr]['Fee Amount'].sum()
    
            delta_avg = fee_df_sel[fee_df_sel['Year'] == least_recent_yr]['Fee Amount'].mean()
        else:   
            delta_ytd = fee_df_sel[(fee_df_sel['Year'] == least_recent_yr) &
                                      (fee_df_sel['Week'] <= max_year_week)]['Fee Amount'].sum()
    
            delta_avg = fee_df_sel[(fee_df_sel['Year'] == least_recent_yr) &
                                      (fee_df_sel['Week'] <= max_year_week)]['Fee Amount'].mean()
    
        # metrics
        ytd_col, yoy_col, avg_col = st.columns(3)
        
        ytd_col.metric(
            label=label_val_ytd,
            value= '${:,}'.format(np.round(most_recent_ytd,2)),
            delta = f"YTD - {least_recent_yr}: {'${:,}'.format(np.round(delta_ytd,2))}",
            delta_color="off"
        )
    
        yoy_col.metric(
            label=f'{label_val_yoy}/{least_recent_yr}',
            value= f"{np.round((most_recent_ytd - delta_ytd)/ delta_ytd * 100,2)}%",
        )
    
        avg_col.metric(
            label=label_val_avg,
            value= '${:,}'.format(np.round(most_recent_avg,2)),
            delta = f"Avg Fee - {least_recent_yr}: {'${:,}'.format(np.round(delta_avg,2))}",
            delta_color="off"
        )
    
        # time series analysis
        # add yoy tabs
        fee_df_sel['Year'] = fee_df_sel['Year'].astype(str)
        fee_df['Year'] = fee_df['Year'].astype(str)
        st.subheader('Fee Trends')
        yoy_w_tab, yoy_m_tab, trend_tab = st.tabs(['Year/Year By Week', 'Year/Year By Month', 'Fee Trend'])
        
        with yoy_w_tab:
            st.altair_chart(alt.Chart(fee_df_sel).mark_bar().encode(
                x=alt.X('Week', axis=alt.Axis(tickMinStep=1),scale=alt.Scale(domain=[1, 53])), y='sum(Fee Amount)',color='Year'), use_container_width=True)
        with yoy_m_tab:
            st.altair_chart(alt.Chart(fee_df_sel).mark_bar().encode(
                x=alt.X('Month', axis=alt.Axis(tickCount=12),scale=alt.Scale(domain=[1, 12])), y='sum(Fee Amount)',color='Year'), use_container_width=True)
        with trend_tab:
            st.altair_chart(alt.Chart(fee_df).mark_line().encode(
                x='Year', y='sum(Fee Amount)',color='Primary Campus'), use_container_width=True)

        # Create the breakdown analysis
        ###############################
        st.subheader("Fee Breakdowns")
        ps_tab, pss_tab, pb_tab = st.tabs(['Fees By Payment Source', 'Fees By Payment Source Sub', 'Fees By Payment Brand'])

        with ps_tab:               
            st.altair_chart(
                    alt.hconcat(
                    alt.Chart(fee_df_sel).mark_bar().encode(
                        alt.X('sum(Fee Amount):Q'),
                        alt.Y('Payment Source:O'),
                        color='Year:N',
                    ),
                    alt.Chart(fee_df_sel).mark_bar().encode(
                        alt.X('mean(Fee Percentage):Q').axis(format='%'),
                        alt.Y('Payment Source:O').title(None),
                        color='Year:N',
                    ))
                    , use_container_width=True)
        with pss_tab:               
            st.altair_chart(
                    alt.hconcat(
                    alt.Chart(fee_df_sel).mark_bar().encode(
                        alt.X('sum(Fee Amount):Q'),
                        alt.Y('Payment Source Sub:O'),
                        color='Year:N',
                    ),
                    alt.Chart(fee_df_sel).mark_bar().encode(
                        alt.X('mean(Fee Percentage):Q').axis(format='%'),
                        alt.Y('Payment Source Sub:O').title(None),
                        color='Year:N',
                    ))
                    , use_container_width=True)
        with pb_tab:               
            st.altair_chart(
                    alt.hconcat(
                    alt.Chart(fee_df_sel).mark_bar().encode(
                        alt.X('sum(Fee Amount):Q'),
                        alt.Y('Payment Brand:O'),
                        color='Year:N',
                    ),
                    alt.Chart(fee_df_sel).mark_bar().encode(
                        alt.X('mean(Fee Percentage):Q').axis(format='%'),
                        alt.Y('Payment Brand:O').title(None),
                        color='Year:N',
                    ))
                    , use_container_width=True)

    except:
        st.write('error')

with forecast_tab:

    fct_explaination_string = '''
    The giving forecast report shows the expected sum of donations for the current year.

    These forecasts are generated by AI models at the primary campus level.

    To ensure your church's forecasts are as accurate as possible, please assign all donors to a campus when appropriate!

    While AI models have shown to be useful in forecasting, please note that these forecasts are probabalistic and cannot foresee future events that may affect your church's donor patterns. Use this data with care and caution. 
    '''
    with forecast_tab.expander("Click to Learn More"):
        st.write(fct_explaination_string)

    
    forecasts_df = conn.query(f'''
    SELECT 
        DONATION_YEAR as "Year",
    	DONATION_MONTH as "Month",
    	DONATION_WEEK as "Week",
        RECEIVED_AT as "Date",
        PRIMARY_CAMPUS as "Primary Campus",
        ACTUAL as "Actual",
        FORECAST as "Forecast",
        LOWER_BOUND as "Lower Bound",
        UPPER_BOUND as "Upper Bound" 
    FROM ANALYTICS.GIVING_FORECASTS_REPORT 
    WHERE YEAR(RECEIVED_AT) <= {max_year} AND 
    YEAR(RECEIVED_AT) >= {max_year - 1}''', ttl=0)
 
    filter_col, col2 = st.columns([.30, .7])

    fct_giving_pc_sel = filter_col.multiselect(
                'Select Forecast By Primary Campus',
                options = pd.unique(forecasts_df['Primary Campus']),
                default = pd.unique(forecasts_df['Primary Campus']),
            )
    

    forecasts_df_sel = forecasts_df.query('`Primary Campus`==@fct_giving_pc_sel')

    
    overview_df = forecasts_df_sel.groupby(['Year', 'Month', 'Week', 'Date'])[['Actual', 'Forecast']].sum().reset_index()
    overview_df = pd.melt(overview_df, id_vars=['Year', 'Month', 'Week', 'Date'], value_vars=['Actual', 'Forecast'], value_name='Donations', var_name = 'Type')

    overview_df['Label'] = overview_df['Year'].astype(str) + " - " + overview_df['Type']

    overview_df = overview_df[(overview_df['Label'] != f'{max_year-1} - Forecast')]
    
    # trend visuals
    ytd_col, forecasted_col, yoy_col = st.columns(3)
    
    ytd_col.metric(
        label=f'YTD Giving - {max_year}',
        value= '${:,}'.format(np.round(overview_df[(overview_df['Type'] == 'Actual') & (overview_df['Year'] == max_year)]['Donations'].sum(),2)),
        delta_color="off"
    )

    forecasted_col.metric(
        label= f'Forecasted Year End Donations - {max_year}',
        value= '${:,}'.format(np.round(overview_df[overview_df.Year == max_year].Donations.sum(),0))
    )

    yoy_col.metric(
        label='Forecast Y/Y Growth',
        value= f"{np.round(((overview_df[overview_df.Year == max_year].Donations.sum()) - (overview_df[overview_df.Year == max_year-1].Donations.sum()))/ (overview_df[overview_df.Year == max_year-1].Donations.sum()) * 100,2)}%",
    )

    
    yoy_w_tab, yoy_m_tab, trend_tab = st.tabs(['Forecasted Year/Year By Week', 'Forecasted Year/Year By Month', 'Forecasted Giving Trend'])
    
    with yoy_w_tab: 
        st.bar_chart(
            data = overview_df.groupby(['Label', 'Week'])['Donations'].sum().reset_index(),
            x = 'Week',
            y = 'Donations',
            color = "Label")

    with yoy_m_tab:
        st.bar_chart(
            data = overview_df.groupby(['Label', 'Month'])['Donations'].sum().reset_index(),
            x = 'Month',
           y = 'Donations',
            color = 'Label')

    with trend_tab:
        st.bar_chart(
            data = overview_df.groupby(['Date', 'Type'])['Donations'].sum().reset_index(),
            x = 'Date',
            y = 'Donations',
            color='Type'
        ) 


with risk_tab:
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
