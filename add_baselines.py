import os
import glob
import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.api import ExponentialSmoothing

# --- Configuration ---
# Directory containing the forecast CSVs to be read from and written to.
OUTPUT_DATA_DIR = "data_preparation/output_data/min_med_max_and_error"

# Configuration for the baseline models
ROLLING_WINDOW_DAYS = 7

# --- Baseline Model Functions ---

def generate_constant_baseline(history_series: pd.Series, forecast_horizon: int) -> pd.Series:
    """
    Generates a constant baseline from the last value of a rolling average, floored at zero.
    """
    smoothed_history = history_series.rolling(
        window=ROLLING_WINDOW_DAYS, min_periods=1
    ).mean().dropna()

    if smoothed_history.empty:
        warnings.warn("Not enough historical data for constant baseline. Returning empty values.")
        return pd.Series([np.nan] * forecast_horizon)

    last_known_value = smoothed_history.iloc[-1]
    forecast = pd.Series([last_known_value] * forecast_horizon)
    return forecast.clip(lower=0)

def generate_damped_trend_baseline(history_series: pd.Series, forecast_horizon: int) -> pd.Series:
    """
    Generates a forecast using Holt's Damped Trend Model, floored at zero.
    """
    if len(history_series) < 3:
        warnings.warn("Not enough historical data for Damped Trend model. Returning empty values.")
        return pd.Series([np.nan] * forecast_horizon)

    try:
        model = ExponentialSmoothing(
            history_series,
            trend='add',
            damped_trend=True,
            seasonal=None
        ).fit()
        forecast = model.forecast(forecast_horizon)
        return forecast.clip(lower=0)
    except Exception as e:
        warnings.warn(f"Damped Trend model failed: {e}. Returning empty values.")
        return pd.Series([np.nan] * forecast_horizon)

# --- Main Processing Logic ---

def process_files():
    """
    Main function to find, process, and update forecast files with baselines.
    """
    search_pattern = os.path.join(OUTPUT_DATA_DIR, "**", "*_error.csv")
    forecast_files = glob.glob(search_pattern, recursive=True)

    if not forecast_files:
        print("Error: No forecast files found. Check the OUTPUT_DATA_DIR path.")
        return

    print(f"Found {len(forecast_files)} forecast files to process.\n")

    for forecast_file in forecast_files:
        try:
            print(f"Processing: {os.path.basename(forecast_file)}")

            # 1. DERIVE CUTOFF DATE from the filename.
            base_name = os.path.basename(forecast_file).replace('_error.csv', '')
            date_str = '_'.join(base_name.split('_')[0:3])
            cutoff_date = pd.to_datetime(date_str, format='%Y_%m_%d')

            # 2. LOAD a single output_data file.
            df = pd.read_csv(forecast_file, index_col=0, parse_dates=True)

            # 3. SPLIT the data within this file for fitting.
            history_series = df[df.index < cutoff_date]['reality'].dropna()

            if history_series.empty:
                print(f"  -> WARNING: No historical 'reality' data found before {cutoff_date} in this file. Skipping.")
                continue

            # 4. Determine the forecast period from the file itself.
            forecast_period = df[df.index >= cutoff_date]
            forecast_horizon = len(forecast_period)

            # 5. Generate the baseline forecasts.
            constant_forecast = generate_constant_baseline(history_series, forecast_horizon)
            damped_trend_forecast = generate_damped_trend_baseline(history_series, forecast_horizon)

            # NEW: If damped trend failed, fill its NaN values with the constant baseline forecast.
            damped_trend_forecast = damped_trend_forecast.fillna(constant_forecast)
            
            # 6. ADD forecasts to the DataFrame and save.
            # Use .loc to assign values only to the forecast period.
            df.loc[df.index >= cutoff_date, 'constant_baseline'] = constant_forecast.values
            df.loc[df.index >= cutoff_date, 'damped_trend_baseline'] = damped_trend_forecast.values
            
            df.to_csv(forecast_file)
            print("  -> Success: Updated file with 'constant' and 'damped_trend' baselines.")

        except Exception as e:
            print(f"  -> ERROR processing {os.path.basename(forecast_file)}: {e}")
        
        print("-" * 20)

if __name__ == "__main__":
    process_files()