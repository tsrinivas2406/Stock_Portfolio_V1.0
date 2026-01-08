import csv
# import mysql.connector

import time as md_time
from datetime import time as dt_time
from datetime import datetime, timedelta

import shutil
import streamlit as st

troubleshoot = False

# File to store the current day's API call counts
CSV_FILE = 'api_call_counts.csv'

# Global variable to store API call counts
api_call_count = {}

# Function to load counts from CSV file
def load_counts_from_csv():
    global api_call_count
    try:
        with open(CSV_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                api_call_count[row['function']] = {
                    'count': int(row['count']),
                    'last_reset': row['last_reset']
                }
    except FileNotFoundError:
        # File not found, initialize counts
        pass

# Function to save counts to CSV file
def save_counts_to_csv():
    global api_call_count
    with open(CSV_FILE, mode='w', newline='') as file:
        fieldnames = ['function', 'count', 'last_reset']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for func_name, data in api_call_count.items():
            writer.writerow({
                'function': func_name,
                'count': data['count'],
                'last_reset': data['last_reset']
            })

# Function to insert counts into MySQL database
def archive_counts_to_mysql():
    global api_call_count
    now = datetime.now().strftime('%Y-%m-%d')
    # MySQL database connection details
    db_config = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'database': 'sigmadb'
    }
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Insert each function's count into the database
    for func_name, data in api_call_count.items():
        query = (
            "INSERT INTO api_counter (date, api_function, count) "
            "VALUES (%s, %s, %s)"
            "ON DUPLICATE KEY UPDATE count = VALUES(count)"
        )
        cursor.execute(query, (data['last_reset'], func_name, data['count']))
    
    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

# Function to reset the counts at midnight
def reset_counts_if_new_day(func_name):
    global api_call_count
    now = datetime.now().strftime('%Y-%m-%d')
    if func_name in api_call_count and now != api_call_count[func_name]['last_reset']:
        # Archive the current day's counts before resetting
        archive_counts_to_mysql()
        # Reset the counts for the new day
        api_call_count[func_name]['count'] = 0
        api_call_count[func_name]['last_reset'] = now
        save_counts_to_csv()

# Function to backup the API Counts and reset 
def reset_api_counters():
    # Define the original file and the new file name with date and time
    original_file = "api_call_counts.csv"
    # previous_datetime = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y_%m_%d_%H_%M")
    previous_datetime = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d_%H_%M")
    new_file = f"api_call_counts_{previous_datetime}.csv"

    try:
        # Copy the file to the new name
        shutil.copy(original_file, new_file)
        st.write(f"Copied {original_file} to {new_file}")

        # Clear the contents of the original file
        with open(original_file, 'w') as file:
            file.truncate(0)
        st.write(f"Cleared the contents of {original_file}")
    except Exception as e:
        st.write(f"An error occurred: {e}")

# Decorator to track API calls
def track_api_call(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        if func_name not in api_call_count:
            api_call_count[func_name] = {'count': 0, 'last_reset': datetime.now().strftime('%Y-%m-%d')}
        reset_counts_if_new_day(func_name)
        api_call_count[func_name]['count'] += 1
        save_counts_to_csv()
        return func(*args, **kwargs)
    return wrapper

# Load counts from CSV at start
load_counts_from_csv()

# ### TEST Function with the decorator to track the API Calls

# @track_api_call
# def fun_1():
#     # Your API call logic here
#     print("API call made by fun_1")


# # Example usage
# fun_1()

# print(api_call_count)

### Troubleshooting and Testing 
if troubleshoot : 
    print(datetime.now())
    previous_datetime = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d_%H_%M")
    print(previous_datetime)

