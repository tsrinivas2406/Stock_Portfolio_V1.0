import pandas as pd
from datetime import datetime, timedelta
from openchart import NSEData
import math


# Initialize and download master data
nse = NSEData()
nse.download()



def get_equity_data(symbol,duration,interval="1d"):
   
    end_date = datetime.now()
    start_date = end_date - timedelta(days=duration)
    
    df = nse.historical(
    symbol=symbol,
    exchange="NSE",
    start=start_date,
    end=end_date,
    interval=interval
    # interval="1m"
    )
    return df

def get_ltp_nse_oc(symbol,duration):


    # ### Original Code ###
    # end_date = datetime.now()
    # start_date = end_date - timedelta(days=duration)
    # #########################
    
    start_date = datetime.now() - timedelta(days=duration)
    end_date = datetime.now() - timedelta(days=duration-1)

    print("-"*60)
    print(f'Start Date  : {start_date}')
    print(f'End Date    : {end_date}')
    
    try : 
        df = nse.historical(
        symbol=symbol,
        exchange="NSE",
        start=start_date,
        end=end_date,
        interval="1d"

        )
        print("-------------get_ltp_nse_oc : Response -----------------")
        print(df)
        print("--------------------------------------------------------")

        ltp_str = df["Close"]
        # ltp = float(ltp_str) ### Deprecated 

        ### New Method to “Take the first element of the Series and convert it to float.”

        if not ltp_str.empty:
            ltp = float(ltp_str.iloc[0])
        else:
            ltp = 0   # or raise an error

        # print(ltp)        
        # print("--------------------------------------------------------")
        return(ltp)
    
    
    except Exception as e:
        print(f'get_ltp_nse_oc : Error:: {e}\n')
        return 0
    
##### Next 2 Functions are a SET     
    
def get_ltp_grid(symbol,duration):
   
    end_date = datetime.now()
    start_date = end_date - timedelta(days=duration)
    
    df = nse.historical(
    symbol=symbol,
    exchange="NSE",
    start=start_date,
    end=end_date,
    interval="1d"
    # interval="1m"
    )
    return df

def get_close_price_grid(stocks, n_days):
    close_series = []
    days = int(math.ceil(n_days * 1.5)+3)
    # print(days)

    for stock in stocks:
        df = get_ltp_grid(stock, days)

        if df is None or df.empty:
            continue

        # Ensure datetime index
        df = df.copy()
        df.index = pd.to_datetime(df.index)

        # Use date only
        df['date'] = df.index.date

        # Take last close per date (handles intraday rows safely)
        daily_close = (
            df.groupby('date')['Close']
            .last()
            .rename(stock)
        )

        close_series.append(daily_close)

    # Combine all stocks into one grid
    close_grid = pd.concat(close_series, axis=1)

    # Sort by date and keep last n days
    close_grid.index = pd.to_datetime(close_grid.index)
    close_grid = close_grid.sort_index().tail(n_days)
    # ### Creating a Transpose 
    # close_grid = close_grid.T
    return close_grid


#######################################################################################
### TEST FUCNTIONS 
#######################################################################################
    
# ### Funtion 1 Test 
# df = get_equity_data("NIFTYBEES",1,"1d")
# print(df)

# ### Funtion 2 Test 
# df = get_ltp_nse_oc("NIFTYBEES",4)
# print(df)


#######################################################################
### Method 2 
#######################################################################

holdings_df = pd.read_csv("stockholdings.csv")

# Unique instruments you actually hold
stock_list = (
    holdings_df["Instrument"]
    .dropna()
    .unique()
    .tolist()
)

n_days = 10

price_grid = get_close_price_grid(stock_list, n_days)
# print(price_grid.T)

qty_df = (
    holdings_df
    .groupby("Instrument")["Tot_Qty"]
    .sum()
)

valid_stocks = qty_df[qty_df != 0].index.tolist()

price_grid = get_close_price_grid(valid_stocks, n_days)

print(price_grid.T)

holding_value_grid = price_grid.mul(qty_df, axis=1)

print(holding_value_grid)