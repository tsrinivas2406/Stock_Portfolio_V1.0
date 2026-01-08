import streamlit as st
import pandas as pd

from fun_api_counter import *
from fun_logging_decorator import *

# Load positions from a CSV file
@track_api_call
@log_function_call
def load_positions(csv_file):
    return pd.read_csv(csv_file)


@track_api_call
@log_function_call
def save_positions(df, csv_file):
    df = df.sort_values(by=['Segment','Leg'],ascending=[False,True])
    df.to_csv(csv_file, index=False)


@track_api_call
@log_function_call
def load_csv(csv_file):
    return pd.read_csv(csv_file)

@track_api_call
@log_function_call
def save_to_csv(df, csv_file):
    df.to_csv(csv_file, index=False)
    print(f'Saved the file {csv_file} successfully !!!' )

