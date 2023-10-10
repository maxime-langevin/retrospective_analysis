import matplotlib as mpl
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from retrospective_analysis.metrics import max_error, mean_difference
from retrospective_analysis.evaluate_scenarios import (
    evaluate_all_scenarios,
    evaluate_all_scenarios_with_dates,
    compute_metrics_all_scenarios,
)

# Set matplotlib style
mpl.rcParams.update(
    {
        "font.family": "serif",
        "axes.titlesize": 40,
        "axes.labelsize": 40,
        "legend.fontsize": 40,
        "pgf.rcfonts": False,
        "figure.dpi": 300.0,
    }
)

mpl.rcParams["axes.unicode_minus"] = False
sns.set(
    font_scale=1.5,
    style="white",
    rc={
        "font.family": "sans-serif",
        "axes.titlesize": 40,
        "axes.labelsize": 40,
        "legend.fontsize": 40,
        "xtick.labelsize": 40,
        "ytick.labelsize": 40,
        "xtick.bottom": True,
        "ytick.left": True,
        "figure.dpi": 300.0,
    },
)

# to change with path suited for you

results_path = "results/"
images_path = "images/"

# divide by 100 to express as % of normalization
new_hosp_normalization = 3040 / 100  # based on data from Paireau et al. publication
icu_normalization = 7000 / 100
idf_icu_normalization = 2600 / 100

metrics = {"MAE": mean_absolute_error, "ME": mean_difference, "Max Error": max_error}

endpoints_normalizations = {
    "ICU": 7000 / 100,
    "idf_icu_normalization": 2600 / 100,
    "New hosp.": 3040 / 100,
}

data_location = {
    "2020/04/28 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2020_04_28_ICU_error.csv",
    "2020/10/30 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2020_10_30_ICU_error.csv",
    "2021/01/16": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_01_16_new_hosp_error.csv",
    "2021/02/02": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_02_02_new_hosp_error.csv",
    "2021/02/08": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_02_08_new_hosp_error.csv",
    "2021/02/23": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_02_23_new_hosp_error.csv",
    "2021/04/26": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_04_26_new_hosp_error.csv",
    "2021/05/21": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_05_21_new_hosp_error.csv",
    "2021/05/21 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2021_05_21_ICU_error.csv",
    "2021/07/26 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2021_07_26_ICU_error.csv",
    "2021/07/26": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_07_26_new_hosp_error.csv",
    "2021/08/05": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_08_05_new_hosp_error.csv",
    "2021/08/05 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2021_08_05_ICU_error.csv",
    "2021/10/04": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_10_04_new_hosp_error.csv",
    "2022/01/07": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2022_01_07_new_hosp_error.csv",
    "2022/01/07 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2022_01_07_ICU_error.csv",
}

normalizations = {
    "2020/04/28 ICU": idf_icu_normalization,
    "2020/10/30 ICU": icu_normalization,
    "2021/01/16": new_hosp_normalization,
    "2021/02/02": new_hosp_normalization,
    "2021/02/08": new_hosp_normalization,
    "2021/02/23": new_hosp_normalization,
    "2021/04/26": new_hosp_normalization,
    "2021/05/21": new_hosp_normalization,
    "2021/05/21 ICU": icu_normalization,
    "2021/07/26 ICU": icu_normalization,
    "2021/07/26": new_hosp_normalization,
    "2021/08/05": new_hosp_normalization,
    "2021/08/05 ICU": icu_normalization,
    "2021/10/04": new_hosp_normalization,
    "2022/01/07": new_hosp_normalization,
    "2022/01/07 ICU": icu_normalization,
}

increasing = {
    "2020/04/28 ICU": False,
    "2020/10/30 ICU": True,
    "2021/01/16": True,
    "2021/02/02": True,
    "2021/02/08": True,
    "2021/02/23": True,
    "2021/04/26": False,
    "2021/05/21": False,
    "2021/05/21 ICU": False,
    "2021/07/26 ICU": True,
    "2021/07/26": True,
    "2021/08/05": True,
    "2021/08/05 ICU": True,
    "2021/10/04": False,
    "2022/01/07": True,
    "2022/01/07 ICU": True,
}

scenario_endpoints = [
    "ICU",
    "ICU",
    "New hosp.",
    "New hosp.",
    "New hosp.",
    "New hosp.",
    "New hosp.",
    "New hosp.",
    "ICU",
    "ICU",
    "New hosp.",
    "New hosp.",
    "ICU",
    "New hosp.",
    "New hosp.",
    "ICU",
]


results = evaluate_all_scenarios(
    data_location, metrics=metrics, normalizations=normalizations, increasing=increasing
)
with open(results_path + "error_metrics.csv", "w", encoding="utf-8-sig") as f:
    results.to_csv(f)

results_with_dates = evaluate_all_scenarios_with_dates(
    data_location, metrics=metrics, normalizations=normalizations, increasing=increasing
)
with open(
    results_path + "error_metrics_stratified_by_dates.csv", "w", encoding="utf-8-sig"
) as f:
    results_with_dates.to_csv(f)

# ------------------------------------------------------------------------------------------------------

data_location = {
    "2020/04/28 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2020_04_28_ICU_error.csv",
    "2020/10/30 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2020_10_30_ICU_error.csv",
    "2021/01/16": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_01_16_new_hosp_error.csv",
    "2021/02/02": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_02_02_new_hosp_error.csv",
    "2021/02/08": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_02_08_new_hosp_error.csv",
    "2021/02/23": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_02_23_new_hosp_error.csv",
    "2021/04/26": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_04_26_new_hosp_error.csv",
    "2021/05/21": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_05_21_new_hosp_error.csv",
    "2021/05/21 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2021_05_21_ICU_error.csv",
    "2021/07/26 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2021_07_26_ICU_error.csv",
    "2021/07/26": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_07_26_new_hosp_error.csv",
    "2021/08/05": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_08_05_new_hosp_error.csv",
    "2021/08/05 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2021_08_05_ICU_error.csv",
    "2021/10/04": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2021_10_04_new_hosp_error.csv",
    "2022/01/07": "data_preparation/output_data/min_med_max_and_error/new_hosp_error/2022_01_07_new_hosp_error.csv",
    "2022/01/07 ICU": "data_preparation/output_data/min_med_max_and_error/ICU_error/2022_01_07_ICU_error.csv",
}

normalizations = {
    "2020/04/28 ICU": idf_icu_normalization,
    "2020/10/30 ICU": icu_normalization,
    "2021/01/16": new_hosp_normalization,
    "2021/02/02": new_hosp_normalization,
    "2021/02/08": new_hosp_normalization,
    "2021/02/23": new_hosp_normalization,
    "2021/04/26": new_hosp_normalization,
    "2021/05/21": new_hosp_normalization,
    "2021/05/21 ICU": icu_normalization,
    "2021/07/26 ICU": icu_normalization,
    "2021/07/26": new_hosp_normalization,
    "2021/08/05": new_hosp_normalization,
    "2021/08/05 ICU": icu_normalization,
    "2021/10/04": new_hosp_normalization,
    "2022/01/07": new_hosp_normalization,
    "2022/01/07 ICU": icu_normalization,
}

endpoints = [
    "ICU",
    "ICU",
    "New hosp.",
    "New hosp.",
    "New hosp.",
    "New hosp.",
    "New hosp.",
    "New hosp.",
    "ICU",
    "ICU",
    "New hosp.",
    "New hosp.",
    "ICU",
    "New hosp.",
    "New hosp.",
    "ICU",
    "ICU",
    "ICU",
]


results = evaluate_all_scenarios(
    data_location, metrics=metrics, normalizations=normalizations, increasing=increasing
)

data_location_self_assessment = {
    "2022/01/07": "data_preparation/source_data/improper_comparisons/improper_comparison_Jan_07_2022.csv",
    "2021/02/02": "data_preparation/source_data/improper_comparisons/improper_comparison_Feb_02_2022.csv",
}

results_self_assessment = evaluate_all_scenarios(
    data_location_self_assessment,
    metrics=metrics,
    normalizations={"2022/01/07": 70.0, "2021/02/02": 70.0},
    increasing={"2022/01/07": True, "2021/02/02": False},
)


full_results = pd.concat([results, results_self_assessment])
dates = list(normalizations.keys())
dates = [x.split()[0] for x in dates]

public = [
    "No",
    "No",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
]
legitimate_comparisons = [
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "Yes",
    "No",
    "No",
    "No",
]


dates.extend(["2022/01/07", "2021/02/02"])
additional_information_df = pd.DataFrame(
    zip(dates, endpoints, public, legitimate_comparisons),
    columns=["Date", "Endpoint", "Public", "Valid assessment"],
)
additional_information_df["Self-assessment by modelers"] = [
    "No",
    "No",
    "No",
    "No",
    "No",
    "No",
    "No",
    "Yes",
    "Yes",
    "No",
    "No",
    "No",
    "No",
    "No",
    "No",
    "No",
    "Yes",
    "Yes",
]

additional_information_df.index = full_results.index

full_results = pd.concat([full_results, additional_information_df], axis=1)

with open(
    results_path + "error_metrics_including_illegitimate_comparisons.csv",
    "w",
    encoding="utf-8-sig",
) as f:
    full_results.to_csv(f)

# ------------------------------------------------------------------------------------------------------

df_low_scenario = compute_metrics_all_scenarios(
    data_location,
    metrics=metrics,
    normalizations=normalizations,
    increasing=increasing,
    scenario_name="min",
)
df_low_scenario["endpoints"] = scenario_endpoints
df_low_scenario["MAE (beds)"] = df_low_scenario["MAE"].values * np.array(
    [endpoints_normalizations[x] for x in scenario_endpoints]
)
df_low_scenario["Max error (beds)"] = df_low_scenario["Max Error"].values * np.array(
    [endpoints_normalizations[x] for x in scenario_endpoints]
)

print(
    df_low_scenario.to_latex(
        formatters={"name": str.upper}, float_format="{:.1f}".format
    )
)

df_median_scenario = compute_metrics_all_scenarios(
    data_location,
    metrics=metrics,
    normalizations=normalizations,
    increasing=increasing,
    scenario_name="med",
)
df_median_scenario["endpoints"] = scenario_endpoints
df_median_scenario["MAE (beds)"] = df_median_scenario["MAE"].values * np.array(
    [endpoints_normalizations[x] for x in scenario_endpoints]
)
df_median_scenario["Max error (beds)"] = df_median_scenario[
    "Max Error"
].values * np.array([endpoints_normalizations[x] for x in scenario_endpoints])

print(
    df_median_scenario.to_latex(
        formatters={"name": str.upper}, float_format="{:.1f}".format
    )
)


df_high_scenario = compute_metrics_all_scenarios(
    data_location,
    metrics=metrics,
    normalizations=normalizations,
    increasing=increasing,
    scenario_name="max",
)
df_high_scenario["endpoints"] = scenario_endpoints
df_high_scenario["MAE (beds)"] = df_high_scenario["MAE"].values * np.array(
    [endpoints_normalizations[x] for x in scenario_endpoints]
)
df_high_scenario["Max error (beds)"] = df_high_scenario["Max Error"].values * np.array(
    [endpoints_normalizations[x] for x in scenario_endpoints]
)

print(
    df_high_scenario.to_latex(
        formatters={"name": str.upper}, float_format="{:.1f}".format
    )
)

display_df = pd.concat(
    [
        df_low_scenario.assign(scenario="Optimist"),
        df_median_scenario.assign(scenario="Median"),
        df_high_scenario.assign(scenario="Pessimist"),
    ],
    axis=0,
)
display_df["Increasing"] = (
    list(increasing.values()) + list(increasing.values()) + list(increasing.values())
)

with open(
    results_path + "error_metrics_stratified_by_scenario_types.csv",
    "w",
    encoding="utf-8-sig",
) as f:
    display_df.to_csv(f)

fig, ax = plt.subplots(figsize=(15, 15))
h = sns.boxplot(data=display_df, y="ME", x="scenario", ax=ax, hue="Increasing")

ax.axhline(y=0, linestyle="--", c="g", label="Unbiased scenario")
ax.set_ylabel("Mean Error")
plt.legend()
"""
fig_path = images_path + "/mean_error_by_scenario_type.pdf"
plt.savefig(fig_path, dpi=300, bbox_inches="tight")
"""
