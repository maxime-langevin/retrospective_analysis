import pandas as pd
import numpy as np
from retrospective_analysis.data_loading import load_dataframe

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
  column_names = ["Average uncertainty", "Max uncertainty", "Global accuracy"]
  for i, (scenario, url) in enumerate(urls.items()):
      normalization = normalizations[scenario]
      df = load_dataframe(url, start_date=scenario.replace('/', '-'))
      dict_results = {}
      dict_results["Average uncertainty"] =  np.mean(df["high"]/normalization - df["low"]/normalization)
      dict_results["Max uncertainty"] = np.max(df["high"]/normalization - df["low"]/normalization)
      dict_results["Global accuracy"] = 100 * np.mean((df["reality"]<=df["high"]) & (df["reality"]>=df["low"]))
      results["Scenario: {}".format(scenario)] = list(dict_results.values())
  return pd.DataFrame.from_dict(results, orient='index', columns=column_names).round(1)


def compute_metrics_all_scenarios(urls, metrics, normalizations, scenario_name = "low", n_days=None, baseline=True):
  results = {}
  column_names = list(metrics.keys())

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
      else:
        dict_results = compute_metrics(df, metrics=metrics, scenario_name = scenario_name, normalization=normalization)
      results["Scenario: {}".format(scenario)] = list(dict_results.values())
  return pd.DataFrame.from_dict(results, orient='index', columns=column_names).round(1)

