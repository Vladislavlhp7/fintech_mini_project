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

def curve_inversion_detector(df, type='2Y-10Y'):
    """
    Detects the yield curve inversion based on the specified type.

    Parameters:
    df (DataFrame): DataFrame containing yield data.
    type (str): Type of yield curve inversion to detect. Default is '2Y-10Y', alternatively '3M-10Y'.
    Returns:
    DataFrame: DataFrame with an additional column indicating inversion.
    """
    if type == '3M-10Y':
        df['3M-10Y'] = df['3M'] - df['10Y']
    elif type == '2Y-10Y':
        df['2Y-10Y'] = df['2Y'] - df['10Y']
    else:
        raise ValueError("Invalid type. Use '2Y-10Y' or '3M-10Y'.")
    df['Inversion'] = np.where(df[type] < 0, 1, 0)
    return df

def yield_curve_inversion_visualisation(df, type='2Y-10Y'):
    """
    Visualizes the yield curve inversion based on the specified type.

    Parameters:
    df (DataFrame): DataFrame containing yield data.
    type (str): Type of yield curve inversion to visualize. Default is '2Y-10Y', alternatively '3M-10Y'.
    """
    df = curve_inversion_detector(df, type)
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df[type], label=type, color='blue')
    plt.axhline(0, color='red', linestyle='--', label='Inversion Threshold')
    plt.fill_between(df.index, df[type], 0, where=(df['Inversion'] == 1), color='red', alpha=0.5)
    plt.title(f'{type} Yield Curve Inversion')
    plt.xlabel('Date')
    plt.ylabel('Spread (%)')
    plt.legend()
    plt.show()

def depth_of_inversion(df, type='2Y-10Y'):
    """
    Calculates the depth of yield curve inversion in 3 buckets: mild, moderate, and severe.
    Parameters:
    df (DataFrame): DataFrame containing yield data.
    type (str): Type of yield curve inversion to calculate. Default is '2Y-10Y', alternatively '3M-10Y'.
    Returns:
    DataFrame: DataFrame with an additional column indicating the depth of inversion.
    """
    if type == '3M-10Y':
        df['3M-10Y'] = df['3M'] - df['10Y']
    elif type == '2Y-10Y':
        df['2Y-10Y'] = df['2Y'] - df['10Y']
    else:
        raise ValueError("Invalid type. Use '2Y-10Y' or '3M-10Y'.")
    
    # Calculate depth of inversion
    df['Depth'] = np.where(df[type] < -0.5, 'Severe',
                           np.where(df[type] < -0.25, 'Moderate', 
                           np.where(df[type] < 0, 'Mild', 'No Inversion')))
    return df

def slope_of_inversion(df, types=['2Y-10Y', '3M-10Y']):
    """
    Calculates the slope of the yield curve inversion.
    Parameters:
    df (DataFrame): DataFrame containing yield data.
    types (list): List of types of yield curve inversion to calculate. Default is ['2Y-10Y', '3M-10Y'].
    Returns:
    DataFrame: DataFrame with an additional column indicating the slope of inversion.
    """
    for type in types:
        df[f"Slope-{type}"] = df[type].diff()
        df[f"Slope-{type}-def"] = np.where(df[f"Slope-{type}"] > 0, 'Steepening', 'Flattening')
    return df

def get_recession_data():
    """
    Fetches the recession data from FRED.
    """
    recession_data = fred.get_series('USREC').to_frame().rename(columns={0: 'Recession'}).dropna()
    return recession_data

def yield_curve_inversion_against_recession_visualization(df, type='2Y-10Y'):
    """
    Visualizes the yield curve inversion against recession periods.

    Parameters:
    df (DataFrame): DataFrame containing yield data and recession periods.
    """
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['10Y'], label='10Y Treasury Yield', color='blue')
    if type == '2Y-10Y':
        plt.plot(df.index, df['2Y'], label='2Y Treasury Yield', color='orange')
        plt.fill_between(df.index, df['2Y'], df['10Y'], where=(df['Inversion'] == 1), color='red', alpha=0.5)
    elif type == '3M-10Y':
        plt.plot(df.index, df['3M'], label='3M Treasury Yield', color='green')
        plt.fill_between(df.index, df['3M'], df['10Y'], where=(df['Inversion'] == 1), color='red', alpha=0.5)
    for i in range(len(df)):
        if df['Recession'].iloc[i] == 1:
            plt.axvspan(df.index[i], df.index[i+1], color='gray', alpha=0.5)
    plt.title(f'{type} Yield Curve Inversion with Recession')
    plt.xlabel('Date')
    plt.ylabel('Yield (%)')
    plt.legend()
    plt.show()

def has_recession_followed(df, type='2Y-10Y', min_period=6, max_period=18):
    """
    Checks if a recession followed the yield curve inversion between the specified periods.
    Parameters:
    df (DataFrame): DataFrame containing yield data.
    type (str): Type of yield curve inversion to check. Default is '2Y-10Y', alternatively '3M-10Y'.
    min_period (int): Minimum number of months before a recession is considered. Default is 6.
    max_period (int): Maximum number of months before a recession is considered. Default is 24.
    Returns:
    DataFrame: DataFrame with an additional column indicating if a recession followed the inversion.
    """
    df["Recession_Followed"] = 0
    df["Recession_Followed_Period"] = np.nan
    for i in range(max_period, 0, -1):
        df['Recession_Followed'] = np.where((df['Inversion'] == 1) & (df['Recession'].shift(-i) == 1), 1, df['Recession_Followed'])
        df['Recession_Followed_Period'] = np.where((df['Inversion'] == 1) & (df['Recession'].shift(-i) == 1), i, df['Recession_Followed_Period'])
    return df

def recession_hit_rate(df, type='2Y-10Y'):
    """
    Calculates the recession hit rate based on the yield curve inversion.
    Parameters:
    df (DataFrame): DataFrame containing yield data.
    type (str): Type of yield curve inversion to calculate. Default is '2Y-10Y', alternatively '3M-10Y'.
    Returns:
    float: Recession hit rate.
    """
    total_inversions = df['Inversion'].sum()
    total_recessions = df['Recession_Followed'].sum()
    
    if total_inversions == 0:
        return 0.0
    else:
        return total_recessions / total_inversions

def get_signal_A(df, type='2Y-10Y'):
    df = curve_inversion_detector(df, type=type)
    df = depth_of_inversion(df, type=type)
    df = slope_of_inversion(df, types=[type])
    return df

def get_signal_B(type='2Y-10Y'):
    df = get_yield_curve_data()
    recession_df = get_recession_data()
    df = df.join(recession_df, how='left')
    df = get_signal_A(df, type=type)
    df = has_recession_followed(df, type=type)
    return df


def simulation() -> dict:
    """
    Simulates the yield curve inversion and recession data.
    """    
    # Fetch the yield curve data
    df = get_yield_curve_data()
    
    # Get the signal B
    df = get_signal_B()
    # print(df.tail())

    hit_rate = recession_hit_rate(df)
    # print(f"Recession Hit Rate: {hit_rate:.2%}")
    
    return {
        "data": df,
        "hit_rate": hit_rate,
    }

simulation()