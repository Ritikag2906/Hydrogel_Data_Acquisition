"""
Instron Mechanical Analysis - Smooth vs Rough Surfaces

Author: Ritika Gupta
Institute: Max Planck Institute for Intelligent Systems

Project:
Smart Soft Sensor Architectures for Multimodal Perception

Description:
Analyzes the Instron mechanical data for the main experimental
conditions and compares smooth and rough surfaces.

Main dataset:
- Smooth surfaces: H10, H20, H30, H50 (Trial 01)
- Rough surfaces: H10, H20, H30, H50 with R30 and R40

Gel and No Testbed data are kept separate and are not included here.

This script uses Instron data only.
"""

import os
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ======================================================
# PROJECT PATHS
# ======================================================

PROJECT_DIR = r"C:\Users\rgupta\Desktop\Master thesis\Hydrogel_Data_Acquisition"

INSTRON_DIR = os.path.join(
    PROJECT_DIR,
    "Dataset",
    "Instron_Data"
)

FIGURES_DIR = os.path.join(
    PROJECT_DIR,
    "Figures",
    "Mechanical_Smooth_vs_Rough"
)

RESULTS_DIR = os.path.join(
    PROJECT_DIR,
    "Analysis",
    "Mechanical_Results"
)

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# ======================================================
# EXPERIMENTAL CONDITIONS
# ======================================================

conditions = [
    ("Smooth", 10, None),
    ("Rough", 10, 30),
    ("Rough", 10, 40),

    ("Smooth", 20, None),
    ("Rough", 20, 30),
    ("Rough", 20, 40),

    ("Smooth", 30, None),
    ("Rough", 30, 30),
    ("Rough", 30, 40),

    ("Smooth", 50, None),
    ("Rough", 50, 30),
    ("Rough", 50, 40)
]


# ======================================================
# FIND CSV FILE
# ======================================================

def find_csv(folder):
    """Find the CSV file inside an Instron export folder."""

    files = glob.glob(
        os.path.join(folder, "*.csv")
    )

    if len(files) == 0:
        return None

    return files[0]


# ======================================================
# READ INSTRON DATA
# ======================================================

def read_instron_file(filepath):
    """Read and clean an Instron CSV file."""

    data = pd.read_csv(filepath)

    required_columns = [
        "Time",
        "Displacement",
        "Force",
        "Compressive strain (Displacement)",
        "Compressive stress"
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
        "Time"
    )

    data = data.drop_duplicates(
        subset="Time"
    )

    return data


# ======================================================
# FIND ALL MAIN FILES
# ======================================================

trial_data = {}
features = []

for surface, hardness, roughness in conditions:

    if surface == "Smooth":

        folder_pattern = os.path.join(
            INSTRON_DIR,
            "SmoothSurface",
            f"Hardness_{hardness}_Trial01*"
        )

    else:

        folder_pattern = os.path.join(
            INSTRON_DIR,
            "RoughSurface",
            f"Hardness_{hardness}_Trialden{roughness}*"
        )

    matching_folders = glob.glob(folder_pattern)

    if len(matching_folders) == 0:
        print(
            f"\nNo folder found for: "
            f"{surface} H{hardness} R{roughness}"
        )
        continue

    csv_file = find_csv(
        matching_folders[0]
    )

    if csv_file is None:
        print(
            f"\nNo CSV found for: "
            f"{surface} H{hardness} R{roughness}"
        )
        continue

    try:
        data = read_instron_file(csv_file)

    except Exception as error:
        print("\nCould not read:")
        print(csv_file)
        print(error)
        continue

    if len(data) < 2:
        continue

    time = data["Time"].to_numpy()
    displacement = data["Displacement"].to_numpy()
    force = data["Force"].to_numpy()

    strain = data[
        "Compressive strain (Displacement)"
    ].to_numpy()

    stress = data[
        "Compressive stress"
    ].to_numpy()

    condition_name = f"{surface}_H{hardness}"

    if roughness is not None:
        condition_name += f"_R{roughness}"

    trial_data[condition_name] = {
        "surface": surface,
        "hardness": hardness,
        "roughness": roughness,
        "time": time,
        "displacement": displacement,
        "force": force,
        "strain": strain,
        "stress": stress,
        "filepath": csv_file
    }

    # Maximum values
    max_force = np.max(force)
    max_displacement = np.max(displacement)
    max_strain = np.max(strain)
    max_stress = np.max(stress)

    # Effective loading stiffness
    displacement_min = np.min(displacement)
    displacement_max = np.max(displacement)

    lower_limit = (
        displacement_min +
        0.20 * (displacement_max - displacement_min)
    )

    upper_limit = (
        displacement_min +
        0.80 * (displacement_max - displacement_min)
    )

    loading_mask = (
        (displacement >= lower_limit) &
        (displacement <= upper_limit)
    )

    if np.sum(loading_mask) >= 2:

        loading_stiffness = np.polyfit(
            displacement[loading_mask],
            force[loading_mask],
            1
        )[0]

    else:

        loading_stiffness = np.nan

    # Mechanical work
    loading_work = np.trapezoid(
        np.abs(force),
        displacement
    )

    features.append({

        "Condition": condition_name,
        "Surface": surface,
        "Hardness": hardness,
        "Roughness Density (%)": roughness,

        "Maximum Force (N)": max_force,
        "Maximum Displacement": max_displacement,
        "Maximum Strain": max_strain,
        "Maximum Stress (MPa)": max_stress,

        "Effective Loading Stiffness (N/unit)": loading_stiffness,

        "Mechanical Work": loading_work
    })


# ======================================================
# FEATURE SUMMARY
# ======================================================

summary = pd.DataFrame(features)

if summary.empty:
    print("\nNo Instron data were found.")
    raise SystemExit

summary = summary.sort_values(
    ["Hardness", "Surface", "Roughness Density (%)"]
)

summary.to_csv(
    os.path.join(
        RESULTS_DIR,
        "Smooth_vs_Rough_Mechanical_Features.csv"
    ),
    index=False
)

print("\n==============================================")
print("INSTRON: SMOOTH VS ROUGH ANALYSIS")
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
# FORCE VS DISPLACEMENT
# One graph for each hardness
# ======================================================

for hardness in [10, 20, 30, 50]:

    plt.figure(figsize=(9, 6))

    for condition_name, trial in trial_data.items():

        if trial["hardness"] != hardness:
            continue

        plt.plot(
            trial["displacement"],
            trial["force"],
            linewidth=1.5,
            label=condition_name
        )

    plt.xlabel("Displacement")
    plt.ylabel("Force (N)")

    plt.title(
        f"Plot 1 - Force vs Displacement: Smooth vs Rough - H{hardness}"
    )

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIGURES_DIR,
            f"H{hardness}_Smooth_vs_Rough_Force_Displacement.png"
        ),
        dpi=300
    )

    plt.close()


# ======================================================
# OLD HARDNESS-BASED PLOTS
# ======================================================
#
# These plots are kept for reference but are commented
# out for now. The current comparison uses surface
# condition on the x-axis.
#
# Original plots:
# - Maximum Force vs Hardness
# - Effective Loading Stiffness vs Hardness
# - Maximum Displacement vs Hardness
# - Maximum Stress vs Hardness
#
# ======================================================


# ======================================================
# NEW SURFACE / ROUGHNESS-BASED PLOTS
# ======================================================
#
# The x-axis represents the surface condition:
# Smooth, R30 and R40.
#
# Each line represents one hardness level.
# This allows the effect of surface condition to be
# compared while keeping hardness constant.
#
# H20 is included again because the H20 measurements
# have now been retaken.
# ======================================================

surface_conditions = ["Smooth", "R30", "R40"]
hardness_levels = [10, 20, 30, 50]


def get_surface_values(feature_column, hardness):
    """Get Smooth, R30 and R40 values for one hardness."""

    values = []

    for surface_condition in surface_conditions:

        if surface_condition == "Smooth":

            row = summary[
                (summary["Surface"] == "Smooth") &
                (summary["Hardness"] == hardness)
            ]

        else:

            roughness = int(surface_condition[1:])

            row = summary[
                (summary["Surface"] == "Rough") &
                (summary["Hardness"] == hardness) &
                (
                    summary["Roughness Density (%)"]
                    == roughness
                )
            ]

        if len(row) > 0:

            values.append(
                row[feature_column].iloc[0]
            )

        else:

            values.append(np.nan)

    return values


# ======================================================
# PLOT 2
# MAXIMUM FORCE VS SURFACE CONDITION
# ======================================================

plt.figure(figsize=(9, 6))

for hardness in hardness_levels:

    values = get_surface_values(
        "Maximum Force (N)",
        hardness
    )

    plt.plot(
        surface_conditions,
        values,
        marker="o",
        linewidth=1.5,
        label=f"H{hardness}"
    )

plt.xlabel("Surface Condition")
plt.ylabel("Maximum Force (N)")

plt.title(
    "Plot 2 - Maximum Force vs Surface Condition"
)

plt.legend(title="Hardness")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "Maximum_Force_vs_Surface_Condition.png"
    ),
    dpi=300
)

plt.close()


# ======================================================
# PLOT 3
# EFFECTIVE LOADING STIFFNESS VS SURFACE CONDITION
# ======================================================

plt.figure(figsize=(9, 6))

for hardness in hardness_levels:

    values = get_surface_values(
        "Effective Loading Stiffness (N/unit)",
        hardness
    )

    plt.plot(
        surface_conditions,
        values,
        marker="o",
        linewidth=1.5,
        label=f"H{hardness}"
    )

plt.xlabel("Surface Condition")
plt.ylabel("Effective Loading Stiffness (N/unit)")

plt.title(
    "Plot 3 - Effective Loading Stiffness vs Surface Condition"
)

plt.legend(title="Hardness")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "Loading_Stiffness_vs_Surface_Condition.png"
    ),
    dpi=300
)

plt.close()


# ======================================================
# PLOT 4
# MAXIMUM DISPLACEMENT VS SURFACE CONDITION
# ======================================================

plt.figure(figsize=(9, 6))

for hardness in hardness_levels:

    values = get_surface_values(
        "Maximum Displacement",
        hardness
    )

    plt.plot(
        surface_conditions,
        values,
        marker="o",
        linewidth=1.5,
        label=f"H{hardness}"
    )

plt.xlabel("Surface Condition")
plt.ylabel("Maximum Displacement")

plt.title(
    "Plot 4 - Maximum Displacement vs Surface Condition"
)

plt.legend(title="Hardness")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "Maximum_Displacement_vs_Surface_Condition.png"
    ),
    dpi=300
)

plt.close()


# ======================================================
# PLOT 5
# MAXIMUM STRESS VS SURFACE CONDITION
# ======================================================

plt.figure(figsize=(9, 6))

for hardness in hardness_levels:

    values = get_surface_values(
        "Maximum Stress (MPa)",
        hardness
    )

    plt.plot(
        surface_conditions,
        values,
        marker="o",
        linewidth=1.5,
        label=f"H{hardness}"
    )

plt.xlabel("Surface Condition")
plt.ylabel("Maximum Stress (MPa)")

plt.title(
    "Plot 5 - Maximum Stress vs Surface Condition"
)

plt.legend(title="Hardness")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_DIR,
        "Maximum_Stress_vs_Surface_Condition.png"
    ),
    dpi=300
)

plt.close()


# ======================================================
# PRINT FEATURE SUMMARY
# ======================================================

print("\n----------------------------------------------")
print("Mechanical feature summary")
print("----------------------------------------------")

print(
    summary[
        [
            "Condition",
            "Maximum Force (N)",
            "Maximum Displacement",
            "Maximum Strain",
            "Maximum Stress (MPa)",
            "Effective Loading Stiffness (N/unit)"
        ]
    ].to_string(index=False)
)

print("\nResults saved to:")
print(RESULTS_DIR)

print("\nFigures saved to:")
print(FIGURES_DIR)

print("\nAnalysis completed.")
