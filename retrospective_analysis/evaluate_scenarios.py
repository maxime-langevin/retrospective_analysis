import pandas as pd
import numpy as np
from retrospective_analysis.data_loading import load_dataframe, moving_average
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

icu_normalization = 7000 / 100
idf_icu_normalization = 2600 / 100


def compute_metrics(df, metrics, scenario_name="low", normalization=1, increasing=True):
    results = {}
    for i, (metric_name, metric) in enumerate(metrics.items()):
        # dubious if non linear function?
        # multiply by 100 to express as % of normalization
        results["Scenario_{}: {}".format(scenario_name, metric_name)] = metric(
            df["reality"] / normalization, df[scenario_name] / normalization
        )
    results["Scenario_{}: {}".format(scenario_name, "Increasing")] = increasing
    return results


def evaluate_all_scenarios(urls, metrics, normalizations, increasing):
    results = {}
    column_names = list(metrics.keys())
    column_names = [
        "Average uncertainty (beds)",
        "MAE (median, beds)",
        "MAE (low, beds)",
        "MAE (high, beds)",
        "Historical peak",
        "MAE (median)",
        "MAE (optimist)",
        "MAE (pessimist)",
        "MAPE (median)",
        "MAPE (optimist)",
        "MAPE (pessimist)",
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

        dict_results["Average uncertainty (beds)"] = np.mean(
            df["max"] / normalization - df["min"] / normalization
        )
        dict_results["MAE (median, beds)"] = mean_absolute_error(
            df["reality"], df["med"]
        )
        dict_results["MAE (low, beds)"] = mean_absolute_error(df["reality"], df["min"])
        dict_results["MAE (high, beds)"] = mean_absolute_error(df["reality"], df["max"])
        dict_results["Historical peak"] = normalization
        dict_results["MAE (median)"] = mean_absolute_error(
            df["reality"] / normalization, df["med"] / normalization
        )
        dict_results["MAE (optimist)"] = mean_absolute_error(
            df["reality"] / normalization, df["min"] / normalization
        )
        dict_results["MAE (pessimist)"] = mean_absolute_error(
            df["reality"] / normalization, df["max"] / normalization
        )
        dict_results["MAPE (median)"] = 100 * mean_absolute_percentage_error(
            df["reality"], df["med"]
        )
        dict_results["MAPE (optimist)"] = 100 * mean_absolute_percentage_error(
            df["reality"], df["min"]
        )
        dict_results["MAPE (pessimist)"] = 100 * mean_absolute_percentage_error(
            df["reality"], df["max"]
        )
        dict_results["Increasing"] = increasing[scenario]
        results[f"Scenario: {scenario} {scenario_type}"] = list(dict_results.values())
    return pd.DataFrame.from_dict(results, orient="index", columns=column_names).round(
        1
    )


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

    """
  if n_days:
    column_names = [x + ' : {} scenario {} days'.format(scenario_name, n_days) for x in column_names]
  else:
    column_names = [x + ' : {} scenario'.format(scenario_name) for x in column_names]
  """

    for i, (scenario, url) in enumerate(urls.items()):
        normalization = normalizations[scenario]
        if normalization == icu_normalization or normalization == idf_icu_normalization:
            scenario_type = "ICU"
        else:
            scenario_type = "New hosp."
        df = load_dataframe(url, start_date=scenario.split()[0].replace("/", "-"))
        df = df.apply(pd.to_numeric)
        if n_days:
            dict_results = compute_metrics(
                df.head(n_days),
                metrics=metrics,
                scenario_name=scenario_name,
                normalization=normalization,
                increasing=increasing,
            )
            dict_results[
                "Scenario_{}: {}".format(scenario_name, "MAPE")
            ] = 100 * mean_absolute_percentage_error(df["reality"], df[scenario_name])
        else:
            dict_results = compute_metrics(
                df,
                metrics=metrics,
                scenario_name=scenario_name,
                normalization=normalization,
                increasing=increasing,
            )
            dict_results[
                "Scenario_{}: {}".format(scenario_name, "MAPE")
            ] = 100 * mean_absolute_percentage_error(df["reality"], df[scenario_name])

        results[f"Scenario: {scenario} {scenario_type}"] = list(dict_results.values())
    return pd.DataFrame.from_dict(results, orient="index", columns=column_names).round(
        1
    )


def evaluate_all_scenarios_with_dates(
    urls, metrics, normalizations, increasing, bins_length=14
):
    results = {}
    column_names = list(metrics.keys())
    column_names = [
        "Scenario",
        "Scenario type",
        "Average uncertainty (beds)",
        "MAE (median, beds)",
        "MAE (low, beds)",
        "MAE (high, beds)",
        "Historical peak",
        "MAE (median)",
        "MAE (optimist)",
        "MAE (pessimist)",
        "MAPE (median)",
        "MAPE (optimist)",
        "MAPE (pessimist)",
        "Increasing",
        "Period",
    ]
    for i, (scenario, url) in enumerate(urls.items()):
        normalization = normalizations[scenario]
        if normalization == icu_normalization or normalization == idf_icu_normalization:
            scenario_type = "ICU"
        else:
            scenario_type = "New hosp."
        normalization = 1
        df = load_dataframe(url, start_date=scenario.split()[0].replace("/", "-"))
        df = df.apply(pd.to_numeric)
        dict_results = {}
        for i in range(int(len(df) / bins_length)):
            dict_results["Scenario"] = scenario
            dict_results["Scenario type"] = scenario_type
            dict_results["Average uncertainty (beds)"] = np.mean(
                df["max"].values[i * bins_length : min((i + 1) * bins_length, len(df))]
                - df["min"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ]
                / normalization
            )
            dict_results["MAE (median, beds)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ],
                df["med"].values[i * bins_length : min((i + 1) * bins_length, len(df))],
            )
            dict_results["MAE (low, beds)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ],
                df["min"].values[i * bins_length : min((i + 1) * bins_length, len(df))],
            )
            dict_results["MAE (high, beds)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ],
                df["max"].values[i * bins_length : min((i + 1) * bins_length, len(df))],
            )
            dict_results["Historical peak"] = normalization
            dict_results["MAE (median)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ]
                / normalization,
                df["med"].values[i * bins_length : min((i + 1) * bins_length, len(df))]
                / normalization,
            )
            dict_results["MAE (low)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ]
                / normalization,
                df["min"].values[i * bins_length : min((i + 1) * bins_length, len(df))]
                / normalization,
            )
            dict_results["MAE (high)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ]
                / normalization,
                df["max"].values[i * bins_length : min((i + 1) * bins_length, len(df))]
                / normalization,
            )

            dict_results["MAPE (median)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ],
                df["med"].values[i * bins_length : min((i + 1) * bins_length, len(df))],
            )
            dict_results["MAPE (low)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ],
                df["min"].values[i * bins_length : min((i + 1) * bins_length, len(df))],
            )
            dict_results["MAPE (high)"] = mean_absolute_error(
                df["reality"].values[
                    i * bins_length : min((i + 1) * bins_length, len(df))
                ],
                df["max"].values[i * bins_length : min((i + 1) * bins_length, len(df))],
            )
            dict_results["Increasing"] = increasing[scenario]
            dict_results["Period"] = f"{i*bins_length} days - {(i+1)*bins_length} days"

            results[
                f"Scenario: {scenario}, period: {i*bins_length} days - {(i+1)*bins_length} days".format(
                    scenario
                )
            ] = list(dict_results.values())

    return pd.DataFrame.from_dict(results, orient="index", columns=column_names).round(
        1
    )
