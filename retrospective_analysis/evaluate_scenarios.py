import pandas as pd
import numpy as np
from retrospective_analysis.data_loading import load_dataframe, moving_average
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

icu_normalization = 7000 / 100
idf_icu_normalization = 2600 / 100


def compute_metrics(df, metrics, scenario_name="low", normalization=1, increasing=True):
    # This helper function remains unchanged as it is already generic.
    results = {}
    for i, (metric_name, metric) in enumerate(metrics.items()):
        # NaNs should be handled before calling this function
        clean_df = df[['reality', scenario_name]].dropna()
        if not clean_df.empty:
            results["Scenario_{}: {}".format(scenario_name, metric_name)] = metric(
                clean_df["reality"] / normalization, clean_df[scenario_name] / normalization
            )
        else:
            results["Scenario_{}: {}".format(scenario_name, metric_name)] = np.nan

    results["Scenario_{}: {}".format(scenario_name, "Increasing")] = increasing
    return results


def evaluate_all_scenarios(urls, metrics, normalizations, increasing):
    results = {}
    column_names = [
        "Average uncertainty (beds)",
        "MAE (median, beds)",
        "MAE (low, beds)",
        "MAE (high, beds)",
        "MAE (constant, beds)",
        "MAE (damped_trend, beds)",
        "Historical peak",
        "MAE (median)",
        "MAE (optimist)",
        "MAE (pessimist)",
        "MAPE (median)",
        "MAPE (optimist)",
        "MAPE (pessimist)",
        "MAPE (constant)",
        "MAPE (damped_trend)",
        "Increasing",
    ]
    
    for i, (scenario, url) in enumerate(urls.items()):
        normalization = normalizations[scenario]
        if normalization == icu_normalization or normalization == idf_icu_normalization:
            scenario_type = "ICU"
        else:
            scenario_type = "New hosp."
        
        df = load_dataframe(url, start_date=scenario.split()[0].replace("/", "-"))
        df = df.apply(pd.to_numeric)
        dict_results = {}

        # --- Calculate metrics robustly by dropping NaNs ---
        # Median
        clean_df_med = df[['reality', 'med']].dropna()
        dict_results["MAE (median, beds)"] = mean_absolute_error(clean_df_med["reality"], clean_df_med["med"])
        dict_results["MAPE (median)"] = 100 * mean_absolute_percentage_error(clean_df_med["reality"], clean_df_med["med"])
        dict_results["MAE (median)"] = mean_absolute_error(df["reality"] / normalization, df["med"] / normalization)
        
        # Low (Optimist)
        clean_df_low = df[['reality', 'min']].dropna()
        dict_results["MAE (low, beds)"] = mean_absolute_error(clean_df_low["reality"], clean_df_low["min"])
        dict_results["MAPE (optimist)"] = 100 * mean_absolute_percentage_error(clean_df_low["reality"], clean_df_low["min"])
        dict_results["MAE (optimist)"] = mean_absolute_error(df["reality"] / normalization, df["min"] / normalization)

        # High (Pessimist)
        clean_df_high = df[['reality', 'max']].dropna()
        dict_results["MAE (high, beds)"] = mean_absolute_error(clean_df_high["reality"], clean_df_high["max"])
        dict_results["MAPE (pessimist)"] = 100 * mean_absolute_percentage_error(clean_df_high["reality"], clean_df_high["max"])
        dict_results["MAE (pessimist)"] = mean_absolute_error(df["reality"] / normalization, df["max"] / normalization)
        
        # Constant Baseline
        if 'constant_baseline' in df.columns:
            clean_df_const = df[['reality', 'constant_baseline']].dropna()
            if not clean_df_const.empty:
                dict_results["MAE (constant, beds)"] = mean_absolute_error(clean_df_const["reality"], clean_df_const["constant_baseline"])
                dict_results["MAPE (constant)"] = 100 * mean_absolute_percentage_error(clean_df_const["reality"], clean_df_const["constant_baseline"])
            else:
                dict_results["MAE (constant, beds)"] = np.nan
                dict_results["MAPE (constant)"] = np.nan
        
        # Damped Trend Baseline
        if 'damped_trend_baseline' in df.columns:
            clean_df_damped = df[['reality', 'damped_trend_baseline']].dropna()
            if not clean_df_damped.empty:
                dict_results["MAE (damped_trend, beds)"] = mean_absolute_error(clean_df_damped["reality"], clean_df_damped["damped_trend_baseline"])
                dict_results["MAPE (damped_trend)"] = 100 * mean_absolute_percentage_error(clean_df_damped["reality"], clean_df_damped["damped_trend_baseline"])
            else:
                dict_results["MAE (damped_trend, beds)"] = np.nan
                dict_results["MAPE (damped_trend)"] = np.nan

        dict_results["Average uncertainty (beds)"] = np.mean(df["max"] - df["min"])
        dict_results["Historical peak"] = normalization
        dict_results["Increasing"] = increasing[scenario]
        
        row = [dict_results.get(col, np.nan) for col in column_names]
        results[f"Scenario: {scenario} {scenario_type}"] = row

    return pd.DataFrame.from_dict(results, orient="index", columns=column_names).round(1)


def compute_metrics_all_scenarios(
    urls,
    metrics,
    normalizations,
    increasing,
    scenario_name="low",
    n_days=None,
    baseline=True,
):
    results = {}
    column_names = list(metrics.keys()) + ["Increasing"] + ["MAPE"]

    for i, (scenario, url) in enumerate(urls.items()):
        normalization = normalizations[scenario]
        if normalization == icu_normalization or normalization == idf_icu_normalization:
            scenario_type = "ICU"
        else:
            scenario_type = "New hosp."
        
        df = load_dataframe(url, start_date=scenario.split()[0].replace("/", "-"))
        df = df.apply(pd.to_numeric)
        
        df_to_eval = df
        if n_days:
            df_to_eval = df.head(n_days)
            
        dict_results = compute_metrics(
            df_to_eval,
            metrics=metrics,
            scenario_name=scenario_name,
            normalization=normalization,
            increasing=increasing[scenario],
        )
        
        clean_df_mape = df_to_eval[['reality', scenario_name]].dropna()
        if not clean_df_mape.empty:
            dict_results["Scenario_{}: {}".format(scenario_name, "MAPE")] = 100 * mean_absolute_percentage_error(
                clean_df_mape["reality"], clean_df_mape[scenario_name]
            )
        else:
            dict_results["Scenario_{}: {}".format(scenario_name, "MAPE")] = np.nan

        results[f"Scenario: {scenario} {scenario_type}"] = list(dict_results.values())
        
    return pd.DataFrame.from_dict(results, orient="index", columns=column_names).round(1)


def evaluate_all_scenarios_with_dates(
    urls, metrics, normalizations, increasing, bins_length=14
):
    results = {}
    column_names = [
        "Scenario", "Scenario type", "Period",
        "Average uncertainty (beds)",
        "MAE (median, beds)", "MAE (low, beds)", "MAE (high, beds)",
        "MAE (constant, beds)", "MAE (damped_trend, beds)",
        "MAPE (median)", "MAPE (optimist)", "MAPE (pessimist)",
        "MAPE (constant)", "MAPE (damped_trend)",
        "Increasing"
    ]
    
    for i, (scenario, url) in enumerate(urls.items()):
        normalization = normalizations[scenario]
        if normalization == icu_normalization or normalization == idf_icu_normalization:
            scenario_type = "ICU"
        else:
            scenario_type = "New hosp."
            
        df = load_dataframe(url, start_date=scenario.split()[0].replace("/", "-"))
        df = df.apply(pd.to_numeric)
        
        for i in range(int(len(df) / bins_length)):
            dict_results = {}
            df_slice = df.iloc[i * bins_length : min((i + 1) * bins_length, len(df))]

            dict_results["Scenario"] = scenario
            dict_results["Scenario type"] = scenario_type
            dict_results["Period"] = f"{i*bins_length} days - {(i+1)*bins_length} days"
            dict_results["Increasing"] = increasing[scenario]
            
            # --- CORRECTED BLOCK START ---
            # Define a clear mapping for each scenario we want to process
            scenarios_to_process = [
                {'col': 'med', 'mae_name': 'median', 'mape_name': 'median'},
                {'col': 'min', 'mae_name': 'low',    'mape_name': 'optimist'},
                {'col': 'max', 'mae_name': 'high',   'mape_name': 'pessimist'},
                {'col': 'constant_baseline', 'mae_name': 'constant', 'mape_name': 'constant'},
                {'col': 'damped_trend_baseline', 'mae_name': 'damped_trend', 'mape_name': 'damped_trend'},
            ]

            for scenario_info in scenarios_to_process:
                col_name = scenario_info['col']
                mae_name = scenario_info['mae_name']
                mape_name = scenario_info['mape_name']

                # Define the exact keys that match the 'column_names' list
                mae_key = f"MAE ({mae_name}, beds)"
                mape_key = f"MAPE ({mape_name})"

                if col_name in df_slice.columns:
                    clean_slice = df_slice[['reality', col_name]].dropna()
                    if not clean_slice.empty:
                        dict_results[mae_key] = mean_absolute_error(clean_slice['reality'], clean_slice[col_name])
                        dict_results[mape_key] = 100 * mean_absolute_percentage_error(clean_slice['reality'], clean_slice[col_name])
                    else:
                        dict_results[mae_key] = np.nan
                        dict_results[mape_key] = np.nan
                else:
                    # Explicitly handle cases where a baseline column might be missing
                    dict_results[mae_key] = np.nan
                    dict_results[mape_key] = np.nan
            # --- CORRECTED BLOCK END ---
            
            dict_results["Average uncertainty (beds)"] = np.mean(df_slice["max"] - df_slice["min"])

            row_key = f"Scenario: {scenario}, period: {i*bins_length}-{(i+1)*bins_length} days"
            results[row_key] = [dict_results.get(col, np.nan) for col in column_names]

    return pd.DataFrame.from_dict(results, orient="index", columns=column_names).round(1)