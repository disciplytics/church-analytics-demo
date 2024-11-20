# Import python packages
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# connect to snowflake
conn = st.connection("snowflake")

# Page Parameters
#st.set_page_config(page_title = "Giving Analytics", layout='wide')
st.header("Giving Analytics")
st.write("Multiple reports to better understand giving in your church.")

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
        
# FEE Tab
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
