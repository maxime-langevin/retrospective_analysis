import numpy as np
import pandas as pd 

# needed to smooth out day-to-day variations 
def moving_average(x, w=7):
    return np.convolve(x, np.ones(w), 'valid') / w

def add_baselines(df, start_date):

  known_data = df[df.index<start_date].reality
  length_of_extrapolation = len(np.where(df.index >= start_date)[0])

  # baseline where we simply impute values using the last observed one 
  last_known_value = known_data[-1]
  last_known_value = moving_average(known_data.values, 7)[-1]
  constant_baseline = [last_known_value for i in range(length_of_extrapolation)]
  
  
  # baseline using Taylor series expansion with first and second order derivatives 
  derivative = np.gradient(moving_average(known_data.values, 7))
  second_order_derivative = np.gradient(derivative)

  first_order_baseline = [last_known_value + derivative[-1]*i for i in range(length_of_extrapolation)]
  second_order_baseline = [last_known_value + derivative[-1]*i + 0.5*second_order_derivative[-1]*i**2 for i in range(length_of_extrapolation)]
  
  df["Constant"] = [x for x in known_data] + constant_baseline
  df["1st order"] = [x for x in known_data] + first_order_baseline
  df["2nd order"] = [x for x in known_data] + second_order_baseline
  
  return df 

def load_dataframe(url, start_date=None, baseline=True, remove_na=True):
  df = pd.read_csv(url, decimal=",")
  df = df.set_index('date')
  
  # to remove in the future 
  # cope with issues in data processing
  try:
    df['median'] = [float(x.replace(',', '.')) if type(x)==str else x for x in df['median']]
  except:
    pass
  df['reality'] = pd.to_numeric(df['reality'])
  # start_date necessary to compute the Taylor-based baselines
  if start_date and baseline:
    df = add_baselines(df, start_date.replace('/', '-'))
  if start_date and remove_na:
    df = df[df.index>start_date.replace('/', '-')]
  if remove_na:
    df = df.dropna(subset=['min', 'med', 'max', 'reality'])
  return df