# SDK Documentation : 
# - https://github.com/jerokpradeep/pya3
# - https://v2api.aliceblueonline.com/libraries

import os

# using explicit imports to overcome the conflict with time module
# import time as md_time
# from datetime import time as dt_time
from datetime import datetime, timedelta 
from time import sleep


from fun_api_counter import *           ### for Function Call Count
from fun_logging_decorator import *     ### for Logging
from pya3 import *                      ### Alice Blue API 

troubleshoot = False

api_key = 'fbVaknK1bLcumL2J1BMGkmZzZ2j472Qj5YKah1zNSVBJI9oBTxLOVluJOj8hsJt3q7skky7y7kpAiOb25cB3MXKRWN7jrlaBaPX6RppPCjXyJmGAT7AID7rSG1FcbPgB'
alice = Aliceblue(user_id='1008410',api_key=api_key)
session_id = alice.get_session_id()

# print(type(session_id))
logging.info(f'Alice Blue API Status : {session_id["stat"]}')

if session_id["stat"] != "Ok" :
    logging.info(f'Session ID : {session_id['sessionID']}')  


# debug = False
# debug = os.environ.get('TROUBLESHOOT')
# print ("Debug:::",debug)


@track_api_call 
@log_function_call
def get_ltp_nse_ab(stock) :
    try:
        token = alice.get_instrument_by_symbol('NSE', stock )
        # if troubleshoot : print(token)

        si = alice.get_scrip_info(token)
        # if troubleshoot : print(si)

        ltp_str = si['Ltp']
        ltp = float(ltp_str)
        # if debug : 
        #     # print("-------------get_ltp_nse_ab : Response -----------------")
        #     # print(si)
        #     # print("--------------------------------------------------------")
        #     pass
        
        # time.sleep(0.5)
        # print(f'{stock} : {ltp}')
        return ltp
    except Exception as e:
        print(f'get_ltp_nse_ab : Error:: {e}\n')
        return 0

## Original Code Function to get Previous Close Price from NSE
@track_api_call
@log_function_call
def get_prev_close_nse(stock) :
    try:
        instrument = alice.get_instrument_by_symbol("NSE", stock)
        from_datetime = datetime.now() - timedelta(days=5)     # From last & days
        to_datetime = datetime.now() - timedelta(days=0)                                   # To now
        interval = "D"       # ["1", "D"]
        indices = False      # For Getting index data

        # logging.info(instrument)
        # logging.info(from_datetime)
        # logging.info(to_datetime)       
        # logging.info(interval)
        # logging.info(indices)


        df_full = alice.get_historical(instrument, from_datetime, to_datetime, interval, indices)
        # logging.info(f'get_prev_close_nse : Full Data Frame : \n {df_full}')

        df = df_full.tail(1)
        # print(f'get_prev_close_nse : {stock}|{df['datetime']}|{df['close']}') #this gives unwanted text in the output
        logging.info(f"get_prev_close_nse : {stock}|{df['datetime'].iloc[0]}|{df['close'].iloc[0]}")

        # print(df_full)
        # print(df)

        prev_close = df['close'].values[0]

        # logging.info(f'get_prev_close_nse : Previous Close Price for {stock} : {prev_close}')
        return prev_close
    
    except Exception as e:
        print(f'get_prev_close_nse : Error:: {e}\n')
        return 0

# ### New Code Function to get Previous Close Price from NSE with Validation Checks : 2025-12-06a

# @track_api_call
# @log_function_call
# def get_prev_close_nse(stock):
#     try:
#         instrument = alice.get_instrument_by_symbol("NSE", stock)
#         if instrument is None:
#             logging.error(f"get_prev_close_nse: No instrument found for stock {stock}")
#             return 0

#         from_datetime = datetime.now() - timedelta(days=7)
#         to_datetime   = datetime.now()
#         interval = "D"
#         indices  = False

#         df_full = alice.get_historical(
#             instrument, from_datetime, to_datetime, interval, indices
#         )

#         # --- VALIDATION CHECKS ---
#         if df_full is None:
#             logging.error("get_prev_close_nse: API returned None (possibly maintenance)")
#             return 0

#         if isinstance(df_full, dict) and df_full.get("stat") == "Not_ok":
#             logging.error(f"get_prev_close_nse: API error response: {df_full}")
#             return 0

#         if not hasattr(df_full, "empty"):
#             logging.error(f"get_prev_close_nse: Unexpected response type: {type(df_full)}")
#             return 0

#         if df_full.empty:
#             logging.error("get_prev_close_nse: Historical data returned empty DataFrame")
#             return 0

#         if "close" not in df_full.columns:
#             logging.error(f"get_prev_close_nse: 'close' column missing. Columns: {df_full.columns}")
#             return 0

#         # --- EXTRACT LAST CLOSE ---
#         prev_close = df_full.tail(1)["close"].iloc[0]

#         return float(prev_close)

#     except Exception as e:
#         logging.exception(f"get_prev_close_nse: Unexpected error: {e}")
#         return 0
    
####################################################################
### TEST Code 
####################################################################

if troubleshoot : 

    si = alice.get_scrip_info(alice.get_instrument_by_symbol('NSE','ICICIBANK'))
    # print(si)
    print(si['Ltp'])
    ltp_num = (float(si['Ltp']))
    ltp_inc = ltp_num + 100

    # print(ltp_inc)
    # print(ltp_num)
    print(get_prev_close_nse('ICICIBANK'))




# if debug:
#     get_ltp_nse_ab('AXISNIFTY')
#     get_ltp_nse_ab('NIFTYBEES')
#     get_ltp_nse_ab('NIF100BEES')
#     get_ltp_nse_ab('GOLDSHARE')

# leg1_pnlleg1_pnl

# print(get_holding_positions())

# # ### Historic Data : NSE Sample Code for testing purpose


# days=10
# exchange='NSE'
# spot_symbol='ICICIBANK'
# interval='1'
# indices=False
# from_date=datetime.now()-timedelta(days=days)
# to_date=datetime.now()
# token=alice.get_instrument_by_symbol(exchange,spot_symbol)
# print(token)
# data=alice.get_historical(token,from_date,to_date,interval,indices)
# data=pd.DataFrame(data)

# # data.to_csv('ICICIBANK.csv')

# # print(data)






