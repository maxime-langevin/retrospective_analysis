import pandas as pd
import numpy as np
from retrospective_analysis.data_loading import load_dataframe
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

icu_normalization = 7000/100 

def compute_metrics(df, metrics, scenario_name = "low", normalization=1):
  results = {}
  for i, (metric_name, metric) in enumerate(metrics.items()):
    # dubious if non linear function? 
    # multiply by 100 to express as % of normalization
    results["Scenario_{}: {}".format(scenario_name, metric_name)] = metric(df["reality"]/normalization, df[scenario_name]/normalization)
  return results 

def evaluate_all_scenarios(urls, metrics, normalizations):
  results = {}
  column_names = list(metrics.keys())
  column_names = ["Average uncertainty", "Max uncertainty", "Global accuracy", "MAE (median)", "MAPE (median)", 
                  "MAPE (optimist)", "MAPE (pessimist)"]
  for i, (scenario, url) in enumerate(urls.items()):
      normalization = normalizations[scenario]
      df = load_dataframe(url, start_date=scenario.replace('/', '-'))
      dict_results = {}
      dict_results["Average uncertainty"] =  np.mean(df["high"]/normalization - df["low"]/normalization)
      dict_results["Max uncertainty"] = np.max(df["high"]/normalization - df["low"]/normalization)
      dict_results["Global accuracy"] = 100 * np.mean((df["reality"]<=df["high"]) & (df["reality"]>=df["low"]))
      dict_results["MAE (median)"] = mean_absolute_error(df["reality"]/normalization, df["median"]/normalization)
      dict_results["MAPE (median)"] = 100 * mean_absolute_percentage_error(df["reality"], df["median"])
      dict_results["MAPE (optimist)"] = 100 * mean_absolute_percentage_error(df["reality"], df["low"])
      dict_results["MAPE (pessimist)"] = 100 * mean_absolute_percentage_error(df["reality"], df["high"])

      results["Scenario: {}".format(scenario)] = list(dict_results.values())
  return pd.DataFrame.from_dict(results, orient='index', columns=column_names).round(1)


def compute_metrics_all_scenarios(urls, metrics, normalizations, scenario_name = "low", n_days=None, baseline=True):
  results = {}
  column_names = list(metrics.keys()) + ["MAPE"]

  """
  if n_days:
    column_names = [x + ' : {} scenario {} days'.format(scenario_name, n_days) for x in column_names]
  else:
    column_names = [x + ' : {} scenario'.format(scenario_name) for x in column_names]
  """
  
  for i, (scenario, url) in enumerate(urls.items()):
      normalization = normalizations[scenario]
      df = load_dataframe(url, start_date=scenario.replace('/', '-'), baseline=baseline)
      if n_days:
        dict_results = compute_metrics(df.head(n_days), metrics=metrics, scenario_name = scenario_name, normalization=normalization)
        dict_results["Scenario_{}: {}".format(scenario_name, "MAPE")] = 100 * mean_absolute_percentage_error(df["reality"], df[scenario_name])
      else:
        dict_results = compute_metrics(df, metrics=metrics, scenario_name = scenario_name, normalization=normalization)
        dict_results["Scenario_{}: {}".format(scenario_name, "MAPE")] = 100 * mean_absolute_percentage_error(df["reality"], df[scenario_name])
    
      results["Scenario: {}".format(scenario)] = list(dict_results.values())
  return pd.DataFrame.from_dict(results, orient='index', columns=column_names).round(1)


def evaluate_all_scenarios_with_dates(urls, metrics, normalizations, bins_length=14):
  results = {}
  column_names = list(metrics.keys())
  column_names = ["Scenario", "Scenario type", "Average uncertainty (beds)", "Max uncertainty", "Global accuracy", "MAE (median, beds)", "Period"]
  for i, (scenario, url) in enumerate(urls.items()):
      normalization = normalizations[scenario]
      if normalization == icu_normalization:
        scenario_type = "ICU"
      else:
        scenario_type = "New hosp."
      normalization = 1
      df = load_dataframe(url, start_date=scenario.replace('/', '-'))
      dict_results = {}
      for i in range(int(len(df)/bins_length)):

          dict_results["Scenario"] = scenario
          dict_results["Scenario type"] = scenario_type
          dict_results["Average uncertainty (beds)"] =  np.mean(df["high"].values[i*bins_length: min((i+1)*bins_length, len(df))]/normalization - df["low"].values[i*bins_length: min((i+1)*bins_length, len(df))]/normalization)
          dict_results["Max uncertainty"] = np.max(df["high"].values[i*bins_length: min((i+1)*bins_length, len(df))]/normalization - df["low"].values[i*bins_length: min((i+1)*bins_length, len(df))]/normalization)
          dict_results["Global accuracy"] = 100 * np.mean((df["reality"]<=df["high"]) & (df["reality"]>=df["low"]))
          dict_results["MAE (median, beds)"] =  mean_absolute_error(df["reality"].values[i*bins_length: min((i+1)*bins_length, len(df))]/normalization, df["median"].values[i*bins_length: min((i+1)*bins_length, len(df))]/normalization)
          dict_results["Period"] = f"{i*bins_length} days - {(i+1)*bins_length} days"
          
          results[f"Scenario: {scenario}, period: {i*bins_length} days - {(i+1)*bins_length} days".format(scenario)] = list(dict_results.values())
          
  return pd.DataFrame.from_dict(results, orient='index', columns=column_names).round(1)