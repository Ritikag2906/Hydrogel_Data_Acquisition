"""
Arduino Electrical Data Analysis

Author: Ritika Gupta
Institute: Max Planck Institute for Intelligent Systems

Project:
Smart Soft Sensor Architectures for Multimodal Perception

Description:
Analyzes voltage and resistance data from the Arduino acquisition
dataset for the main experimental conditions.

Main dataset:
- Smooth surfaces: H10, H20, H30, H50 (T01 only)
- Rough surfaces: H10, H20, H30, H50 with 30% and 40% roughness

Gel and No Testbed data are kept as reference experiments.

This script performs electrical-only analysis.
Mechanical data and synchronization are handled separately.
"""

import os
import glob
import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ======================================================
# PROJECT PATHS
# ======================================================

PROJECT_DIR = r"C:\Users\rgupta\Desktop\Master thesis\Hydrogel_Data_Acquisition"

DATASET_DIR = os.path.join(
    PROJECT_DIR,
    "Dataset",
    "Arduino_Instron_Data"
)

FIGURES_DIR = os.path.join(
    PROJECT_DIR,
    "Figures",
    "Arduino"
)

RESULTS_DIR = os.path.join(
    PROJECT_DIR,
    "Analysis",
    "Arduino_Results"
)

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# ======================================================
# EXPERIMENTAL CONDITIONS
# ======================================================

hardnesses = [10, 20, 30, 50]

smooth_conditions = [
    "Smooth_H10",
    "Smooth_H20",
    "Smooth_H30",
    "Smooth_H50"
]

rough_conditions = [
    "Rough_H10_R30",
    "Rough_H10_R40",
    "Rough_H20_R30",
    "Rough_H20_R40",
    "Rough_H30_R30",
    "Rough_H30_R40",
    "Rough_H50_R30",
    "Rough_H50_R40"
]


# ======================================================
# HELPER FUNCTIONS
# ======================================================

def read_arduino_file(filepath):
    """Read and clean one Arduino CSV file."""

    data = pd.read_csv(filepath)

    required_columns = [
        "Time (s)",
        "Voltage (V)",
        "Resistance (Ohm)"
    ]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"Missing column '{column}' in:\n{filepath}"
            )

    data = data[required_columns].copy()

    for column in required_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data = data.dropna()

    data = data.sort_values(
        "Time (s)"
    )

    data = data.drop_duplicates(
        subset="Time (s)"
    )

    return data


def get_condition(filepath):
    """Determine the experimental condition from the folder structure."""

    path_parts = [
        part.lower()
        for part in Path(filepath).parts
    ]

    lower_path = str(filepath).lower()

    # Smooth surface
    if "smoothsurface" in path_parts:

        match = re.search(
            r"hardness[_ ]?(10|20|30|50)",
            lower_path
        )

        if match:
            hardness = match.group(1)
            return f"Smooth_H{hardness}"

    # Rough surface
    if "roughsurface" in path_parts:

        rough_match = re.search(
            r"rough_h(10|20|30|50)_r(30|40)",
            lower_path
        )

        if rough_match:
            hardness = rough_match.group(1)
            density = rough_match.group(2)

            return f"Rough_H{hardness}_R{density}"

    return None


def is_main_trial(filepath, condition):
    """Select the trials used in the main dataset."""

    filename = os.path.basename(filepath).lower()

    if condition.startswith("Smooth"):
        # Smooth: use T01 only
        return (
            "t01" in filename
            or "trial01" in filename
        )

    if condition.startswith("Rough"):
        # Rough: use the available experimental trial
        return True

    return False


# ======================================================
# FIND DATA FILES
# ======================================================

all_files = glob.glob(
    os.path.join(
        DATASET_DIR,
        "**",
        "*.csv"
    ),
    recursive=True
)

print("\nArduino files found:", len(all_files))


# ======================================================
# READ MAIN DATASET
# ======================================================

results = []
trial_data = {}

for filepath in all_files:

    condition = get_condition(filepath)

    if condition is None:
        continue

    if condition not in (
        smooth_conditions +
        rough_conditions
    ):
        continue

    if not is_main_trial(filepath, condition):
        continue

    try:
        data = read_arduino_file(filepath)

    except Exception as error:
        print("\nCould not read:")
        print(filepath)
        print(error)
        continue

    if len(data) < 2:
        continue

    time = data["Time (s)"].to_numpy()
    voltage = data["Voltage (V)"].to_numpy()
    resistance = data["Resistance (Ohm)"].to_numpy()

    duration = time[-1] - time[0]

    if duration > 0:
        sampling_rate = (len(time) - 1) / duration
    else:
        sampling_rate = 0

    # Initial recorded value
    # The current acquisition starts around the beginning
    # of the compression experiment, so this is called
    # initial resistance rather than a true pre-load baseline.
    n_initial = max(
        1,
        int(0.05 * len(resistance))
    )

    R_initial = np.median(
        resistance[:n_initial]
    )

    V_initial = np.median(
        voltage[:n_initial]
    )

    R_final = np.median(
        resistance[-n_initial:]
    )

    V_final = np.median(
        voltage[-n_initial:]
    )

    delta_R = R_final - R_initial

    if R_initial != 0:
        normalized_delta_R = (
            delta_R / R_initial
        ) * 100
    else:
        normalized_delta_R = np.nan

    delta_V = V_final - V_initial

    if V_initial != 0:
        normalized_delta_V = (
            delta_V / V_initial
        ) * 100
    else:
        normalized_delta_V = np.nan

    resistance_range = (
        np.max(resistance) -
        np.min(resistance)
    )

    voltage_range = (
        np.max(voltage) -
        np.min(voltage)
    )

    trial_id = os.path.splitext(
        os.path.basename(filepath)
    )[0]

    trial_data[trial_id] = {
        "condition": condition,
        "filepath": filepath,
        "time": time,
        "voltage": voltage,
        "resistance": resistance
    }

    results.append({

        "Trial ID": trial_id,
        "Condition": condition,

        "Duration (s)": duration,
        "Samples": len(data),
        "Sampling Rate (Hz)": sampling_rate,

        "Initial Resistance (Ohm)": R_initial,
        "Final Resistance (Ohm)": R_final,
        "Delta R (Ohm)": delta_R,
        "Delta R/R0 (%)": normalized_delta_R,

        "Resistance Mean (Ohm)": np.mean(resistance),
        "Resistance SD (Ohm)": np.std(resistance),
        "Resistance Min (Ohm)": np.min(resistance),
        "Resistance Max (Ohm)": np.max(resistance),
        "Resistance Range (Ohm)": resistance_range,

        "Initial Voltage (V)": V_initial,
        "Final Voltage (V)": V_final,
        "Delta V (V)": delta_V,
        "Delta V/V0 (%)": normalized_delta_V,

        "Voltage Mean (V)": np.mean(voltage),
        "Voltage SD (V)": np.std(voltage),
        "Voltage Min (V)": np.min(voltage),
        "Voltage Max (V)": np.max(voltage),
        "Voltage Range (V)": voltage_range
    })


# ======================================================
# SUMMARY TABLE
# ======================================================

summary = pd.DataFrame(results)

if summary.empty:
    print("\nNo main Arduino trials were found.")
    print("Check the dataset path and folder names.")
    raise SystemExit

summary["Hardness"] = summary["Condition"].str.extract(
    r"H(\d+)"
).astype(float)

summary["Surface"] = np.where(
    summary["Condition"].str.startswith("Smooth"),
    "Smooth",
    "Rough"
)

summary["Roughness Density (%)"] = (
    summary["Condition"]
    .str.extract(r"R(\d+)$")
)

summary["Roughness Density (%)"] = pd.to_numeric(
    summary["Roughness Density (%)"],
    errors="coerce"
)

summary = summary.sort_values(
    ["Hardness", "Surface", "Roughness Density (%)"]
)

summary.to_csv(
    os.path.join(
        RESULTS_DIR,
        "Arduino_Electrical_Features.csv"
    ),
    index=False
)

print("\n==============================================")
print("ARDUINO ELECTRICAL ANALYSIS")
print("==============================================")
print(
    f"Main trials analyzed: {len(summary)}"
)

print("\nConditions:")
print(
    summary["Condition"].to_string(
        index=False
    )
)


# ======================================================
# PLOT 1
# RESISTANCE VS TIME
# ======================================================

for condition in (
    smooth_conditions +
    rough_conditions
):

    condition_trials = [
        trial for trial in trial_data.values()
        if trial["condition"] == condition
    ]

    if len(condition_trials) == 0:
        continue

    plt.figure(figsize=(10, 6))

    for trial in condition_trials:

        plt.plot(
            trial["time"],
            trial["resistance"] / 1000,
            linewidth=1.2,
            label=os.path.basename(
                trial["filepath"]
            )
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Resistance (kΩ)")
    plt.title(
        f"{condition} - Resistance Response"
    )

    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIGURES_DIR,
            f"{condition}_Resistance_vs_Time.png"
        ),
        dpi=300
    )

    plt.close()


# ======================================================
# PLOT 2
# NORMALIZED RESISTANCE VS TIME
# ======================================================

for condition in (
    smooth_conditions +
    rough_conditions
):

    condition_trials = [
        trial for trial in trial_data.values()
        if trial["condition"] == condition
    ]

    if len(condition_trials) == 0:
        continue

    plt.figure(figsize=(10, 6))

    for trial in condition_trials:

        resistance = trial["resistance"]

        n_initial = max(
            1,
            int(0.05 * len(resistance))
        )

        R_initial = np.median(
            resistance[:n_initial]
        )

        if R_initial == 0:
            continue

        normalized_resistance = (
            (resistance - R_initial) /
            R_initial
        ) * 100

        plt.plot(
            trial["time"],
            normalized_resistance,
            linewidth=1.2
        )

    plt.axhline(
        0,
        linewidth=0.8,
        linestyle="--"
    )

    plt.xlabel("Time (s)")
    plt.ylabel("ΔR/R₀ (%)")
    plt.title(
        f"{condition} - Normalized Resistance Response"
    )

    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIGURES_DIR,
            f"{condition}_Normalized_Resistance.png"
        ),
        dpi=300
    )

    plt.close()


# ======================================================
# PLOT 3
# INITIAL RESISTANCE
# ======================================================

plt.figure(figsize=(10, 6))

for condition in (
    smooth_conditions +
    rough_conditions
):

    values = summary.loc[
        summary["Condition"] == condition,
        "Initial Resistance (Ohm)"
    ] / 1000

    if len(values) == 0:
        continue

    x = np.full(
        len(values),
        list(
            smooth_conditions +
            rough_conditions
        ).index(condition)
    )

    plt.scatter(
        x,
        values,
        s=70
    )

plt.xticks(
    range(
        len(
            smooth_conditions +
            rough_conditions
        )
    ),
    smooth_conditions +
    rough_conditions,
    rotation=45,
    ha="right"
)

plt.ylabel("Initial Resistance (kΩ)")
plt.title("Initial Resistance by Condition")

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "Initial_Resistance_by_Condition.png"
    ),
    dpi=300
)

plt.close()


# ======================================================
# PLOT 4
# NORMALIZED RESISTANCE RESPONSE
# ======================================================

plt.figure(figsize=(10, 6))

condition_order = (
    smooth_conditions +
    rough_conditions
)

for condition in condition_order:

    values = summary.loc[
        summary["Condition"] == condition,
        "Delta R/R0 (%)"
    ]

    if len(values) == 0:
        continue

    x = np.full(
        len(values),
        condition_order.index(condition)
    )

    plt.scatter(
        x,
        values,
        s=70
    )

plt.axhline(
    0,
    linewidth=0.8,
    linestyle="--"
)

plt.xticks(
    range(len(condition_order)),
    condition_order,
    rotation=45,
    ha="right"
)

plt.ylabel("ΔR/R₀ (%)")
plt.title("Normalized Resistance Change by Condition")

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "Normalized_Resistance_by_Condition.png"
    ),
    dpi=300
)

plt.close()


# ======================================================
# PLOT 5
# VOLTAGE VS TIME
# ======================================================

for condition in (
    smooth_conditions +
    rough_conditions
):

    condition_trials = [
        trial for trial in trial_data.values()
        if trial["condition"] == condition
    ]

    if len(condition_trials) == 0:
        continue

    plt.figure(figsize=(10, 6))

    for trial in condition_trials:

        plt.plot(
            trial["time"],
            trial["voltage"],
            linewidth=1.2
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title(
        f"{condition} - Voltage Response"
    )

    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIGURES_DIR,
            f"{condition}_Voltage_vs_Time.png"
        ),
        dpi=300
    )

    plt.close()


# ======================================================
# PLOT 6
# SAMPLING RATE
# ======================================================

plt.figure(figsize=(10, 6))

for condition in condition_order:

    values = summary.loc[
        summary["Condition"] == condition,
        "Sampling Rate (Hz)"
    ]

    if len(values) == 0:
        continue

    x = np.full(
        len(values),
        condition_order.index(condition)
    )

    plt.scatter(
        x,
        values,
        s=70
    )

plt.xticks(
    range(len(condition_order)),
    condition_order,
    rotation=45,
    ha="right"
)

plt.ylabel("Sampling Rate (Hz)")
plt.title("Sampling Rate Across Main Experiments")

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "Sampling_Rate_by_Condition.png"
    ),
    dpi=300
)

plt.close()


# ======================================================
# PRINT SUMMARY
# ======================================================

print("\n----------------------------------------------")
print("Electrical feature summary")
print("----------------------------------------------")

print(
    summary[
        [
            "Condition",
            "Initial Resistance (Ohm)",
            "Delta R/R0 (%)",
            "Resistance SD (Ohm)",
            "Sampling Rate (Hz)"
        ]
    ].to_string(index=False)
)

print("\nResults saved to:")
print(RESULTS_DIR)

print("\nFigures saved to:")
print(FIGURES_DIR)

print("\nAnalysis completed.")
