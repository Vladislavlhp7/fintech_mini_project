from fredapi import Fred
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

from dotenv import load_dotenv
import os
import datetime

# Load environment variables from .env file
load_dotenv()

# Get the FRED API key from environment variables
FRED_API_KEY = os.getenv("FRED_API_KEY")
# Initialize the Fred API client
fred = Fred(api_key=FRED_API_KEY)

yield_mapping = {
    '1M': 'GS1M',
    '3M': 'GS3M',
    '6M': 'GS6M',
    '1Y': 'GS1',
    '2Y': 'GS2',
    '5Y': 'GS5',
    '10Y': 'GS10',
    '30Y': 'GS30', 
}


def get_yield_curve_data(start_date=None, end_date=None):
    """
    Fetches the yield curve data from FRED for the specified date range.
    """
    # Fetch the yield curve data
    yield_curve_data = {}
    for key, value in yield_mapping.items():
        yield_curve_data[key] = fred.get_series(value, start_date, end_date)

    # Convert to DataFrame
    df = pd.DataFrame(yield_curve_data)
    df.index = pd.to_datetime(df.index)
    return df

df = get_yield_curve_data()
print(df.head())