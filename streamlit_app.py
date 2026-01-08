print("-"*100)
print("Starting Srinivas Portfolio V1 Application")
print("-"*100)

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
# import mysql.connector
import os
import json
import random
import altair as alt            ### for the Real-time Chart
import base64                   ### for PositionFiles Tab 

# Using explicit imports to overcome the conflict with time module
# import time
# from datetime import datetime, timedelta

import time as md_time
from datetime import time as dt_time
from datetime import datetime, timedelta

import logging
import os

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s',
    level=logging.INFO
)

# import plotly.graph_objs as go  ### for OHLC Stock Chart
# import plotly.figure_factory as ff
# import plotly.offline as pyo    ### for Payof Graph

# import yfinance as yf

from breeze_connect import BreezeConnect
import numpy as np


#####################################################################################################################################################
### APP SETTINGS : 
#####################################################################################################################################################

st.set_page_config(
    page_title="Srinivas Portfolio V1",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",     
    )

### --------------------Custom Function Import --------------------------

### --------------------Custom Function Import --------------------------

from fun_positions import *         ### CSV Load Operations 
from fun_aliceblue_api import *     ### to get the LTP from Alice Blue API
from fun_mfapi import *             ### MFAPI Functions

### ---------------------------------------------------------------------

#####################################################################################################################################################
### SITE Header : Logo , Name , Layout 
#####################################################################################################################################################

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "logo_sigma01_large.png")

def path(*parts):
    return os.path.join(BASE_DIR, *parts)


# st.image('logo_sigma01_large.png', caption='Sigma Engine',width=30) ### with Caption for other Use
col1,col2 = st.columns([1,17])
col1.image(logo_path,width=50)
col2.header("Srinivas Portfolio",divider='rainbow')


stocks_tab,mf_tab,perf_tab = st.tabs(["Equity","MutualFunds","Performance"])

time_now = datetime.now()

print(">>>>>>>>>>>> Run at : ",time_now)

import asyncio
import aiohttp

async def get_ltp_nse_ab2(stock, session):
    from datetime import time
    try:
        token = await asyncio.to_thread(alice.get_instrument_by_symbol, 'NSE', stock)
        si = await asyncio.to_thread(alice.get_scrip_info, token)
        ltp_str = si['Ltp']
        
        logging.info(f'({stock}|{ltp_str})')  # Log stock and LTP  

        ltp = float(ltp_str)
        return ltp
    except Exception as e:
        print(f'get_ltp_nse_ab2 : Error:: {e}\n')
        return 0


# Async function to fetch LTPs
async def fetch_all_ltp_async(mf_df):
    async with aiohttp.ClientSession() as session:     
        tasks = []
        for stock in mf_df['Instrument']:
            # Ensure the task is awaited in a future object
            tasks.append(get_ltp_nse_ab2(stock, session))
            # logging.info(f"          {stock} : getting LTP ... ")
        
    # Gather results
    ltp_list = await asyncio.gather(*tasks)
    return ltp_list


# Function to run the async function and update DataFrame
def update_ltp_column(mf_df):
    # Run the async fetch function
    ltp_list = asyncio.run(fetch_all_ltp_async(mf_df))

    print(f"LTP List : {ltp_list}")

    # Update the dataframe with the new LTP values
    mf_df['LTP'] = ltp_list
    return

def refresh_data() :
    csv_file_4 = "stockholdings.csv"
    mf_df = load_csv(path(csv_file_4))     
    
    print("***[01] Load Portfolio CSV")
    
    ### Calculate :: Previous Close 
    mf_df['Prev_Close'] = mf_df['Instrument'].apply(get_prev_close_nse)
    
    logging.info("***[04] Get Previous Close Price") 
    # logging.info(f">>>>> TATASTEEL Previous Close {get_prev_close_nse("TATASTEEL")}")

    # Call the update function
    update_ltp_column(mf_df)
    
    # print("***[05] Get LTP")
    save_to_csv(mf_df,path(csv_file_4))
 

with stocks_tab:

    Ac1,Ac2,Ac3 = st.columns([1,8,1])
    Bc1,Bc2,Bc3 = st.columns([1,8,1])
    Cc1,Cc2,Cc3 = st.columns([1,8,1])

    with Ac3:
        troubleshoot = st.toggle("Troubleshoot")


    with Ac2:
        print(100*"-")
        print(f"### Reload at :{time_now}")

        ### Refresh Stock Holdings Data
        refresh_data()
        logging.info("New Data Loaded ")

        ###-----------------------------------------------------------------------------

        ### This CSV load is not required always. It is in the format similar to Zerodha Holdings CSV File

        logging.info(BASE_DIR)    

        csv_file_4 = "stockholdings.csv"
        # mf_df = load_csv(csv_file_4)  
        mf_df = load_csv(path(csv_file_4))
        

        logging.info("***[01] Load Portfolio CSV")

        ### Calculating Total Qty = Qty + Pledged. Qty
        mf_df['Tot_Qty'] = (mf_df['Qty.'] + mf_df['Plg_Qty'])
        logging.info("***[02] Calculate Total Qty")

        ### Calculate :: Invested Value
        mf_df['Invest_Value'] = (mf_df['Avg_Cost'] * mf_df['Tot_Qty']).round(0)
        logging.info("***[03b] Calculate Invested Value")

        ### Calculate :: Day Gain / Loss 
        mf_df["Day_PnL"] = (mf_df['LTP'] - mf_df['Prev_Close']) * mf_df['Tot_Qty']

        # Calculate the average of the 'Qty' column - Not used anywhere 
        qty_average = mf_df['Tot_Qty'].mean()

        ### Calculate :: Current Value 
        mf_df['Current_Value'] = (mf_df['Tot_Qty'] * mf_df['LTP']).round(0)

        ### Calculate :: PNL 
        mf_df['PnL'] = (mf_df['Current_Value'] - mf_df['Invest_Value']).round(2)

        mf_df['Last_Updated'] = time_now

        # ### ::: Troubleshooting
        # st.write(mf_df)

        # Method 1 :: Holdings Table in Data Editor 

        # edited_df_stock_portfolio = st.data_editor(data=mf_df,height=800,column_config=column_config)            
        
        # Aggregates 
        current_value_sum = mf_df['Current_Value'].sum().round(0)
        invested_value_sum = mf_df['Invest_Value'].sum().round(0)
        total_pnl = mf_df['PnL'].sum().round(0)
        day_pnl = mf_df['Day_PnL'].sum().round(0)

        logging.info("***[06] Calculate Aggregates")

        # ### Final Save to stockholdings.csv File
        # save_to_csv(mf_df,path(csv_file_4))

    with Ac1:
        
        st.text_input("Invested Value :",invested_value_sum)
        st.text_input("Current Value :",current_value_sum)
        st.text_input("PNL :",total_pnl) 
        st.text_input("Day PNL :",day_pnl) 
        # show_data_bt_pnl = st.toggle("Show PNL Data")
        edit_holdings = st.toggle("Edit Holdings")
        refresh_holdings = st.button("Refresh Holdings")

        print(refresh_holdings)

        if refresh_holdings :
            st.rerun()
            

    if edit_holdings:

        # Define column configurations
        column_config2 = {
            'PnL': {
                'type': 'currency',
                'currency': 'INR',  # Specify the currency
                'format': '₹{:.2f}'  # Custom format for Indian Rupee
            }
        }
 
        with Ac2:
            
            ### Calculating Total Qty = Qty + Pledged. Qty
            mf_df['Tot_Qty'] = (mf_df['Qty.'] + mf_df['Plg_Qty'])
            print("***[02] Calculate Total Qty")

            edited_df_stock_portfolio = st.data_editor(data=mf_df,height=800,column_config=column_config2)
                   


        with Ac3 :    

            if st.button("Save Portfolio"):
                ### Following use of code is very useful to apply function in a dataframe
                edited_df_stock_portfolio['Tot_Qty'] = (mf_df['Qty.'] + mf_df['Plg_Qty'])

                edited_df_stock_portfolio['Prev_Close'] = mf_df['Instrument'].apply(get_prev_close_nse)
                edited_df_stock_portfolio['LTP'] = mf_df['Instrument'].apply(get_ltp_nse_ab)
                edited_df_stock_portfolio['Current_Value'] = (mf_df['Tot_Qty'] * mf_df['LTP']).round(0)

                # ### Calculate :: Previous Close 
                # mf_df['Prev_Close'] = mf_df['Instrument'].apply(get_prev_close_nse)
                # ### Calculate :: Day Gain / Loss 
                # mf_df["Day_PnL"] = (mf_df['Prev_Close'] - mf_df['LTP']) * mf_df['Tot_Qty']

                # Sort the portfolio in ascending order by column Symbol Name 
                edited_df_stock_portfolio = edited_df_stock_portfolio.sort_values(by="Instrument")

                # Reorder Columns in the Data Frame
                # df = df[["symbol", "open", "close", "volume"]]
                edited_df_stock_portfolio = edited_df_stock_portfolio[["Instrument","Qty.","Plg_Qty","Tot_Qty","Avg_Cost","LTP",
                                                                       "Current_Value","Invest_Value","PnL","Prev_Close","Day_PnL","Type","Last_Updated"]]

                ### Save the Data Back into the CSV File
                save_to_csv(edited_df_stock_portfolio,path(csv_file_4))
                
                # st.rerun()  # Rerun the script to refresh the table
    else :
        with Ac2 :

            # Method 2 :: Holdings Table with Dataframe and HTML Formating 


            # Define a function to apply the style to a specific column
            def highlight_negatives(val):
                color = 'red' if val < 0 else 'green'
                return f'color: {color}'

            # Apply the style to the 'PnL' column only
            # To format the PnL Value to 2 Decimal Points = .format({'PnL': '{:.2f}'})
            
            mf_df = mf_df[["Instrument","Qty.","Plg_Qty","Tot_Qty","Avg_Cost","LTP",
                                   "Current_Value","Invest_Value","PnL","Prev_Close","Day_PnL","Type","Last_Updated"]]

            styled_df = mf_df.style.map(highlight_negatives, subset=['PnL','Day_PnL']).format({'PnL': '{:.2f}','Day_PnL':'{:.2f}','Prev_Close':'{:.2f}'})
            
            ### To format the DataFrame to show 2 Decimals Only 
            styled_df = styled_df.format({'Avg_Cost': '{:.2f}','LTP':'{:.2f}','Current_Value':'{:.0f}','Invest_Value':'{:.0f}','PnL': '{:.2f}','Day_PnL':'{:.2f}','Prev_Close':'{:.2f}'})


            st.dataframe(styled_df,height=800,width='stretch')
    
    # sleep(10)
    # st.rerun()

######################################################################################################################################################
### Mutual Fund Selector Tab
######################################################################################################################################################

with mf_tab:
        st.title("Mutual Fund Portfolio Dashboard")

        Ac1,Ac2 = st.columns([2,12])   ## Add MF Section
        Bc1,Bc2 = st.columns([2,12])   ## MF Holdings Section  
        Cc1,Cc2 = st.columns([2,12])   ## MF Chart Section

        
        ### Resources 
        ### Daily NAV Download : https://www.amfiindia.com/spages/NAVAll.txt

        with Bc1:
            ################ MF Side Bar ###############
            
            mf_add = st.toggle("Add Mutual Fund")
            clear_mf = st.button("Clear MF Holdings")
            if clear_mf :
                ## Reset input field
                qty = 0.0  # Reset qty after adding
                selected_fund_name = ""  # Reset selection
                st.rerun()
            

 
  
        with Ac2:
            ############### Add Mutual Fund to Portfolio ###############

            # Fetch mutual funds data
            data = get_mutual_funds()
            funds = {fund["schemeName"]: fund["schemeCode"] for fund in data}

            selected_fund_name = ""
            
            if mf_add :
                st.subheader("Add Mutual Fund to Portfolio")
                
                # Dropdown to select mutual fund
                selected_fund_name = st.selectbox("Select a Mutual Fund", [""] +list(funds.keys()))
                
                # Columns for displaying selected fund details
                Col1,Col2,Col3,Col4,Col5 = st.columns([1,4,1,1,1])

                # Display selected mutual fund's code
                if selected_fund_name != "":
                    selected_fund_code = funds[selected_fund_name]

                    csv_file = "mf_holdings.csv"   # your existing CSV

                    # ------- Input fields for new record -------
                    scheme_code     = Col1.text_input("Scheme Code",value=selected_fund_code)
                    scheme_name     = Col2.text_input("Scheme Name",value=selected_fund_name)
                    latest_nav      = Col3.text_input("NAV",value=(get_latest_nav(scheme_code)))
                    qty             = Col4.number_input("Qty", min_value=0.0, step=1.0)
                    invested_value  = Col5.text_input("Invested Value",value="0")
                    latest_date     = time_now.strftime("%Y-%m-%d")
                    
                    # current_value = st.text_input("Current Value",value="0")

                    # ------- Button to append -------
                    if st.button("Add Record"):
                        new_row = {
                            "Scheme_Code": scheme_code,
                            "Scheme_Name": scheme_name,
                            "Qty": qty,
                            "Invested_Value": invested_value,
                            "Latest_Date": latest_date,
                        }
                        
                        df = pd.read_csv(csv_file)
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        df.to_csv(csv_file, index=False)

                        st.success("Record added successfully!")

            ############### End of Mutual Fund Selector ###############


        with Bc2:
            ############### Mutual Fund Portfolio Display ###############    
            ### This CSV load is not required always. It is in the format similar to Zerodha Holdings CSV File

            csv_file_5 = "mf_holdings.csv"
            mf_df = load_csv(path(csv_file_5))

            # Define column configurations
            column_config = {
                'PnL': {
                    'type': 'currency',
                    'currency': 'INR',  # Specify the currency
                    'format': '₹{:.2f}'  # Custom format for Indian Rupee
                }
            }

            mf_df['Scheme_Name'] = mf_df['Scheme_Code'].apply(get_scheme_name)
            mf_df['Latest_NAV'] = mf_df['Scheme_Code'].apply(get_latest_nav)
            # Calculate : Current Value
            mf_df['Current_Value'] = (mf_df['Qty'] * mf_df['Latest_NAV']).round(0)
            mf_df['Avg. NAV'] = (mf_df['Invested_Value'] / mf_df['Qty']).round(3)
            mf_df['PnL'] = (mf_df['Current_Value'] - mf_df['Invested_Value']).round(0)
            mf_df['Latest_Date'] = time_now.strftime("%Y-%m-%d")


            # edited_df_mf_portfolio = st.data_editor(data=mf_df,height=400,column_config=column_config)
            # mf_df = st.data_editor(data=mf_df,height=600,column_config=column_config) # Static Height
            ht = len(mf_df) * 35 + 60  # Dynamic height based on number of rows    
            mf_df = st.data_editor(data=mf_df,height=ht,column_config=column_config)   # dynamic Height


            # Aggregates 

            #current_value_sum = mf_df['Current_Value'].sum().round(0) # gives error if 'Current Value' is Integer
            current_value_sum = round(mf_df['Current_Value'].sum(),0)

            # invested_value_sum = mf_df['Invested_Value'].sum().round(0)   #gives error if 'Invested_Value' is Integer
            invested_value_sum = round(mf_df['Invested_Value'].sum(),0) 
         
            total_pnl = round(mf_df['PnL'].sum())

            # day_pnl = mf_df['Day_PnL'].sum().round(0)

            # ### Final Save to stockholdings.csv File
            # save_to_csv(mf_df,csv_file_4)

            
            
            save_mf = st.button("Save MF Portfolio")

            if save_mf :
                # print(edited_df_mf_portfolio)

                ### Following use of code is very useful to apply function in a dataframe
                # save_to_csv(edited_df_mf_portfolio,csv_file_5)
                save_to_csv(mf_df,path(csv_file_5))
                md_time.sleep(2)
                save_to_csv(mf_df,path(csv_file_5))

                # st.write("MF Portfolio Saved Successfully !")  
                st.html("<p style='color:green; font-size:20px;'>MF Portfolio Saved Successfully !</p>")
                # st.write("🟢 MF Portfolio Saved Successfully !")

        with Bc1:        
            st.text_input("Invested Value :",invested_value_sum)
            st.text_input("Current Value :",current_value_sum)
            st.text_input("PNL :",total_pnl) 
            # st.text_input("Day PNL :",day_pnl) 


        with Cc1:
            chart       = st.toggle("Show Chart")
            duration    = st.slider("Duration (Years)",min_value=1, max_value=20, value=3, step=1,key='timeframe')
            show_data   = st.toggle("Show Data")  
            

        
        with Cc2:

            if chart:

                # Dropdown showing all MF names
                mf_name = st.selectbox("Select Mutual Fund", mf_df['Scheme_Name'].tolist())
                # st.write(f"mf_name : {mf_name}")

                # Retrieve corresponding mf_code
                mf_code = mf_df.loc[mf_df['Scheme_Name'] == mf_name, 'Scheme_Code'].values[0]

                # st.write(f"mf_code : {mf_code}")
                


                # # Dropdown to select mutual fund
                # mf_name = st.selectbox("Select a Mutual Fund", [""] +list(funds.keys()))

                # Fetch and display historical data
                historical_data = get_historical_data(mf_code)
                historical_navs = historical_data["data"] if "data" in historical_data else []

                if historical_navs:
                    # Convert historical data to DataFrame
                    df = pd.DataFrame(historical_navs)
                    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
                    df['nav'] = df['nav'].astype(float)
                    
                    # Remove rows where 'nav' is 0
                    df = df[df['nav'] != 0]

                    # Truncate the Data
                    # duration in Years from the Input
                    df = df.head(duration*365)   ## Last n Days Data

                    # Display DataFrame as table
                    st.write("Historical NAV Data:")

                    ### Chart 01 : Display Simple Historical NAV Data Line Chart                     
                    # Optionally, display the historical data in a line chart
                    # st.line_chart(df.set_index('date')['nav'])

                    ### Chart 02 : Altair Chart with Y-Axis Scale Control
                    
                    # Determine Y-Axis Scale based on min and max NAV values                    
                    nav_min = round(df['nav'].min(), 2) * 0.9
                    nav_max = round(df['nav'].max(), 2) * 1.1

                    chart = alt.Chart(df,height=550).mark_line().encode(
                        x='date:T',
                        y=alt.Y('nav:Q', scale=alt.Scale(domain=[nav_min,nav_max ]) ),   ## Set Y-Axis Scale Here
                    )

                    st.altair_chart(chart, width='stretch',)

                    if show_data :
                        st.dataframe(df)  # Use st.dataframe to display a table

                else:
                    st.write("No historical data available.")
with perf_tab :
    """
    # :material/query_stats: Indian Stock Market - Dashboard

    """

    ""  # Add some space.



    cols = st.columns([1, 3])
    # Will declare right cell later to avoid showing it when no data.
