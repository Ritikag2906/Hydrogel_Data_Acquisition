# Multimodal Feature Analysis
# ---------------------------
#
# This script analyses the synchronized Arduino and Instron
# measurements collected from the hydrogel sensor.
#
# The main purpose is to look at the relationship between the
# electrical response of the sensor and the mechanical loading.
#
# The analysis is done for four substrate hardness levels:
#
#       H10
#       H20
#       H30
#       H50
#
# For each hardness, the following surface conditions are
# compared:
#
#       Smooth
#       R30
#       R40
#
# The script first reads the synchronized CSV files and
# extracts resistance, force, displacement and time.
#
# For the resistance signal, the initial resistance R0 is
# calculated from the first 5% of the recorded data.
#
# The change in resistance is then calculated as:
#
#       ΔR = R - R0
#
# The script also calculates an SNR value based on the initial
# recorded noise and the maximum absolute change in resistance.
#
# The H20-R30 measurement contains a large electrical artifact.
# Values above the defined threshold are excluded from the
# analysis, but the original synchronized CSV file is not changed.
#
# The main graphs produced are:
#
#       1. ΔR vs Force
#       2. ΔR vs Displacement
#
# Both loading and unloading are kept in the graphs so that the
# complete compression cycle can be seen.
#
# A rolling median is only used to make the plotted curves easier
# to read. The original data are not modified.
#
# In addition, the script creates an SNR bar chart comparing the
# different surface conditions and hardness levels.
#
# The calculated SNR values are also saved as a CSV file for
# further analysis.
#
# All figures and analysis results are saved in the corresponding
# folders inside the thesis project.
#
# The raw synchronized CSV files are never changed.


from pathlib import Path
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. FOLDER SETUP
# ============================================================

PROJECT_ROOT = Path(
    r"C:\Users\rgupta\Desktop\Master thesis\Hydrogel_Data_Acquisition"
)

INPUT_FOLDER = PROJECT_ROOT / "Analysis" / "Synchronized_Data"

FIGURE_FOLDER = (
    PROJECT_ROOT
    / "Figures"
    / "Multimodal"
    / "Response_Curves"
)

DISPLACEMENT_FIGURE_FOLDER = (
    PROJECT_ROOT
    / "Figures"
    / "Multimodal"
    / "DeltaR_vs_Displacement"
)

SNR_FIGURE_FOLDER = (
    PROJECT_ROOT
    / "Figures"
    / "Multimodal"
    / "SNR"
)

RESULT_FOLDER = (
    PROJECT_ROOT
    / "Analysis"
    / "Multimodal_Results"
)

FIGURE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

DISPLACEMENT_FIGURE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

SNR_FIGURE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

RESULT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. EXPERIMENTAL CONDITIONS
# ============================================================

CONDITIONS = [
    "Smooth_H10",
    "Smooth_H20",
    "Smooth_H30",
    "Smooth_H50",

    "Rough_H10_R30",
    "Rough_H10_R40",

    "Rough_H20_R30",
    "Rough_H20_R40",

    "Rough_H30_R30",
    "Rough_H30_R40",

    "Rough_H50_R30",
    "Rough_H50_R40",
]

SURFACE_ORDER = [
    "Smooth",
    "R30",
    "R40"
]

HARDNESS_ORDER = [
    10,
    20,
    30,
    50
]


# ============================================================
# 3. GRAPH STYLE
# ============================================================

SURFACE_COLORS = {
    "Smooth": "#4C8DCA",
    "R30": "#D36B91",
    "R40": "#62A884",
}

HARDNESS_COLORS = {
    10: "#A9C8E8",
    20: "#BDA9DF",
    30: "#E0A9BB",
    50: "#A9CDAF",
}

TEXT_COLOR = "#30343B"
GRID_COLOR = "#D7DCE2"


plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 16,
    "axes.labelsize": 12.5,
    "xtick.labelsize": 10.5,
    "ytick.labelsize": 10.5,
    "legend.fontsize": 10,
    "figure.dpi": 120,
    "savefig.dpi": 300,

    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 1.0,

    "text.color": TEXT_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "axes.titlecolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
})


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def get_condition(file_name):
    """Identify the experimental condition from the file name."""

    name = file_name.lower()

    hardness_match = re.search(
        r"h(10|20|30|50)",
        name
    )

    if hardness_match is None:
        return None

    hardness = hardness_match.group(1)

    roughness_match = re.search(
        r"r(30|40)",
        name
    )

    if roughness_match:
        roughness = roughness_match.group(1)

        return (
            f"Rough_H{hardness}_R{roughness}"
        )

    if "smooth" in name:
        return f"Smooth_H{hardness}"

    return None


def get_condition_name(hardness, surface):
    """Create the condition name."""

    if surface == "Smooth":

        return f"Smooth_H{hardness}"

    return (
        f"Rough_H{hardness}_{surface}"
    )


def find_column(data, possible_names):
    """Find a column using several possible names."""

    columns = {
        str(col).strip().lower(): col
        for col in data.columns
    }

    for name in possible_names:

        if name.lower() in columns:

            return columns[name.lower()]

    return None


def prepare_data(data, condition):
    """Prepare one synchronized trial."""

    data = data.copy()

    data.columns = [
        str(col).strip()
        for col in data.columns
    ]

    # --------------------------------------------------------
    # Find resistance column
    # --------------------------------------------------------

    resistance_col = find_column(
        data,
        [
            "Resistance",
            "Resistance (Ohm)",
            "Resistance (Ω)"
        ]
    )

    if resistance_col is None:
        return None


    # --------------------------------------------------------
    # Find force column
    # --------------------------------------------------------

    force_col = find_column(
        data,
        [
            "Force",
            "Force (N)"
        ]
    )

    if force_col is None:
        return None


    # --------------------------------------------------------
    # Find displacement column
    # --------------------------------------------------------

    displacement_col = find_column(
        data,
        [
            "Displacement",
            "Displacement (mm)"
        ]
    )

    if displacement_col is None:
        return None


    # --------------------------------------------------------
    # Find time column
    # --------------------------------------------------------

    time_col = find_column(
        data,
        [
            "Time",
            "Time (s)"
        ]
    )


    # --------------------------------------------------------
    # Convert to numerical values
    # --------------------------------------------------------

    data["Resistance_analysis"] = pd.to_numeric(
        data[resistance_col],
        errors="coerce"
    )

    data["Force_analysis"] = pd.to_numeric(
        data[force_col],
        errors="coerce"
    )

    data["Displacement_analysis"] = pd.to_numeric(
        data[displacement_col],
        errors="coerce"
    )

    if time_col is not None:

        data["Time_analysis"] = pd.to_numeric(
            data[time_col],
            errors="coerce"
        )

    else:

        data["Time_analysis"] = np.arange(
            len(data)
        )


    # ========================================================
    # H20-R30 ELECTRICAL ARTIFACT
    # ========================================================

    # The H20-R30 trial contains an obvious electrical
    # acquisition artifact at the beginning of the signal.
    #
    # The raw CSV is NOT changed.
    #
    # The invalid resistance values are excluded only
    # from this analysis.

    if condition == "Rough_H20_R30":

        data.loc[
            data["Resistance_analysis"].abs() > 500000,
            "Resistance_analysis"
        ] = np.nan


    # --------------------------------------------------------
    # Remove invalid resistance values
    # --------------------------------------------------------

    data = data.dropna(
        subset=[
            "Resistance_analysis"
        ]
    ).reset_index(drop=True)


    if len(data) < 20:

        return None


    # ========================================================
    # CALCULATE ΔR
    # ========================================================

    # R0 = median of the first 5% of the recorded signal.
    #
    # This is the initial recorded resistance and not a
    # true unloaded baseline.

    n_initial = max(
        5,
        int(len(data) * 0.05)
    )

    initial_values = (
        data["Resistance_analysis"]
        .iloc[:n_initial]
    )

    initial_resistance = (
        initial_values.median()
    )


    # ΔR = R - R0

    data["Delta_R"] = (
        data["Resistance_analysis"]
        - initial_resistance
    )


    # ========================================================
    # CALCULATE SNR
    # ========================================================

    # The first 5% of the recorded signal is used as the
    # initial reference/noise region.
    #
    # SNR is calculated from the peak absolute electrical
    # response relative to the standard deviation of this
    # initial recorded region.
    #
    # This is an initial-recorded-noise-based SNR estimate,
    # not a true unloaded SNR.

    noise_std = initial_values.std()

    peak_delta_r = (
        data["Delta_R"]
        .abs()
        .max()
    )

    if noise_std > 0 and not np.isnan(noise_std):

        snr_ratio = (
            peak_delta_r / noise_std
        )

        snr_db = (
            20 * np.log10(snr_ratio)
        )

    else:

        snr_ratio = np.nan
        snr_db = np.nan


    data.attrs["Initial_Resistance"] = initial_resistance
    data.attrs["Noise_SD"] = noise_std
    data.attrs["Peak_Delta_R"] = peak_delta_r
    data.attrs["SNR_Ratio"] = snr_ratio
    data.attrs["SNR_dB"] = snr_db


    return data


# ============================================================
# 5. READ SYNCHRONIZED DATA
# ============================================================

set_graph_style = None

csv_files = sorted(
    INPUT_FOLDER.rglob("*.csv")
)

print(
    f"Synchronized CSV files found: "
    f"{len(csv_files)}"
)


prepared_trials = {}


for file_path in csv_files:

    condition = get_condition(
        file_path.stem
    )

    if condition not in CONDITIONS:

        print(
            f"Skipping file: "
            f"{file_path.name}"
        )

        continue


    print(
        f"Reading: {condition} "
        f"-> {file_path.name}"
    )


    raw_data = pd.read_csv(
        file_path
    )


    prepared_data = prepare_data(
        raw_data,
        condition
    )


    if prepared_data is None:

        print(
            f"  Could not prepare "
            f"{condition}"
        )

        continue


    prepared_trials[
        condition
    ] = prepared_data


# ============================================================
# 6. ΔR VS FORCE — ALL HARDNESS LEVELS
# ============================================================

# Create one graph for each hardness level:
#
#     H10
#     H20
#     H30
#     H50
#
# Each graph compares:
#
#     Smooth
#     R30
#     R40
#
# The complete compression cycle is retained:
#
#     loading + unloading
#
# ΔR remains signed:
#
#     ΔR = R - R0
#
# Negative ΔR therefore means that resistance decreased
# relative to the initial recorded resistance.


for hardness in HARDNESS_ORDER:

    print(
        f"\nCreating ΔR vs Force plot for H{hardness}..."
    )


    # --------------------------------------------------------
    # Create figure
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )


    # --------------------------------------------------------
    # Plot all surface conditions for this hardness
    # --------------------------------------------------------

    for surface in SURFACE_ORDER:

        condition = get_condition_name(
            hardness,
            surface
        )

        if condition not in prepared_trials:

            print(
                f"  Missing: {condition}"
            )

            continue


        data = prepared_trials[
            condition
        ].copy()


        plot_data = data.dropna(
            subset=[
                "Force_analysis",
                "Delta_R"
            ]
        ).copy()


        if len(plot_data) < 10:

            print(
                f"  Not enough data: {condition}"
            )

            continue


        # Keep experimental time order.
        # This is important because the graph represents
        # the complete loading and unloading cycle.

        plot_data = plot_data.sort_values(
            "Time_analysis"
        ).reset_index(drop=True)


        # ----------------------------------------------------
        # Smooth only for visualisation
        # ----------------------------------------------------

        delta_r_smooth = (
            plot_data["Delta_R"]
            .rolling(
                window=21,
                center=True,
                min_periods=1
            )
            .median()
        )


        # ----------------------------------------------------
        # Plot ΔR against actual force
        # ----------------------------------------------------

        ax.plot(
            plot_data["Force_analysis"],
            delta_r_smooth / 1000,
            linewidth=2.5,
            color=SURFACE_COLORS[surface],
            label=surface
        )


    # --------------------------------------------------------
    # Reference line at ΔR = 0
    # --------------------------------------------------------

    ax.axhline(
        0,
        color="#777777",
        linewidth=0.9,
        linestyle="--",
        alpha=0.65
    )


    # --------------------------------------------------------
    # Labels and formatting
    # --------------------------------------------------------

    ax.set_title(
        f"ΔR vs Force — Full Compression Cycle — H{hardness}",
        pad=14
    )

    ax.set_xlabel(
        "Force (N)"
    )

    ax.set_ylabel(
        "ΔR (kΩ)"
    )


    ax.legend(
        title="Surface condition",
        frameon=True
    )


    ax.grid(
        True,
        color=GRID_COLOR,
        alpha=0.60,
        linewidth=0.8
    )

    ax.set_axisbelow(True)


    plt.tight_layout()


    # --------------------------------------------------------
    # Save figure
    # --------------------------------------------------------

    output_file = (
        FIGURE_FOLDER
        / f"H{hardness}_DeltaR_vs_Force.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    print(
        f"  Saved: {output_file.name}"
    )


# ============================================================
# 6.1 NOTE
# ============================================================

# Normalized force is intentionally not used.
#
# The multimodal analysis keeps the physical force value
# in Newtons so that the relationship between mechanical
# loading and electrical response remains directly visible.
#
# The raw synchronized CSV files are never modified.


# ============================================================
# 7. ΔR VS DISPLACEMENT — ALL HARDNESS LEVELS
# ============================================================

# Create one graph for each hardness level:
#
#     H10
#     H20
#     H30
#     H50
#
# Each graph compares:
#
#     Smooth
#     R30
#     R40
#
# The complete compression cycle is retained:
#
#     loading + unloading
#
# ΔR remains signed:
#
#     ΔR = R - R0
#
# The displacement is taken directly from the synchronized
# Instron data.


for hardness in HARDNESS_ORDER:

    print(
        f"\nCreating ΔR vs Displacement plot for H{hardness}..."
    )


    # --------------------------------------------------------
    # Create figure
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )


    # --------------------------------------------------------
    # Plot all surface conditions for this hardness
    # --------------------------------------------------------

    for surface in SURFACE_ORDER:

        condition = get_condition_name(
            hardness,
            surface
        )

        if condition not in prepared_trials:

            print(
                f"  Missing: {condition}"
            )

            continue


        data = prepared_trials[
            condition
        ].copy()


        plot_data = data.dropna(
            subset=[
                "Displacement_analysis",
                "Delta_R"
            ]
        ).copy()


        if len(plot_data) < 10:

            print(
                f"  Not enough data: {condition}"
            )

            continue


        # Keep experimental time order so that loading and
        # unloading remain visible in the response curve.

        plot_data = plot_data.sort_values(
            "Time_analysis"
        ).reset_index(drop=True)


        # ----------------------------------------------------
        # Smooth only for visualisation
        # ----------------------------------------------------

        delta_r_smooth = (
            plot_data["Delta_R"]
            .rolling(
                window=21,
                center=True,
                min_periods=1
            )
            .median()
        )


        # ----------------------------------------------------
        # Plot ΔR against displacement
        # ----------------------------------------------------

        ax.plot(
            plot_data["Displacement_analysis"],
            delta_r_smooth / 1000,
            linewidth=2.5,
            color=SURFACE_COLORS[surface],
            label=surface
        )


    # --------------------------------------------------------
    # Reference line at ΔR = 0
    # --------------------------------------------------------

    ax.axhline(
        0,
        color="#777777",
        linewidth=0.9,
        linestyle="--",
        alpha=0.65
    )


    # --------------------------------------------------------
    # Labels and formatting
    # --------------------------------------------------------

    ax.set_title(
        f"ΔR vs Displacement — Full Compression Cycle — H{hardness}",
        pad=14
    )

    ax.set_xlabel(
        "Displacement (mm)"
    )

    ax.set_ylabel(
        "ΔR (kΩ)"
    )


    ax.legend(
        title="Surface condition",
        frameon=True
    )


    ax.grid(
        True,
        color=GRID_COLOR,
        alpha=0.60,
        linewidth=0.8
    )

    ax.set_axisbelow(True)


    plt.tight_layout()


    # --------------------------------------------------------
    # Save figure
    # --------------------------------------------------------

    output_file = (
        DISPLACEMENT_FIGURE_FOLDER
        / f"H{hardness}_DeltaR_vs_Displacement.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    print(
        f"  Saved: {output_file.name}"
    )


# ============================================================
# 7.1 NOTE
# ============================================================

# The raw synchronized CSV files are not modified.
# Smoothing is used only for visualisation.


# ============================================================
# 7. SIGNAL-TO-NOISE RATIO BY SURFACE CONDITION
# ============================================================

# Create one grouped bar chart showing SNR for:
#
#     Smooth
#     R30
#     R40
#
# for each hardness level:
#
#     H10
#     H20
#     H30
#     H50
#
# Each bar represents one experimental condition.


snr_rows = []


for hardness in HARDNESS_ORDER:

    for surface in SURFACE_ORDER:

        condition = get_condition_name(
            hardness,
            surface
        )

        if condition not in prepared_trials:
            continue

        data = prepared_trials[condition]

        snr_rows.append({
            "Hardness": hardness,
            "Surface condition": surface,
            "Condition": condition,
            "SNR ratio": data.attrs.get(
                "SNR_Ratio",
                np.nan
            ),
            "SNR (dB)": data.attrs.get(
                "SNR_dB",
                np.nan
            ),
            "Noise SD (Ohm)": data.attrs.get(
                "Noise_SD",
                np.nan
            ),
            "Peak |Delta R| (Ohm)": data.attrs.get(
                "Peak_Delta_R",
                np.nan
            ),
        })


snr_results = pd.DataFrame(
    snr_rows
)


# Save the SNR values used for the graph.
snr_results.to_csv(
    RESULT_FOLDER / "SNR_Features.csv",
    index=False
)


# ------------------------------------------------------------
# Create grouped bar chart
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(10, 6)
)


x = np.arange(
    len(SURFACE_ORDER)
)

bar_width = 0.19


for i, hardness in enumerate(HARDNESS_ORDER):

    values = []

    for surface in SURFACE_ORDER:

        row = snr_results[
            (snr_results["Hardness"] == hardness)
            &
            (
                snr_results["Surface condition"]
                == surface
            )
        ]

        if len(row) == 0:

            values.append(np.nan)

        else:

            values.append(
                row["SNR (dB)"].iloc[0]
            )


    positions = (
        x
        + (i - 1.5) * bar_width
    )


    ax.bar(
        positions,
        values,
        width=bar_width,
        color=HARDNESS_COLORS[hardness],
        edgecolor="white",
        linewidth=0.8,
        label=f"H{hardness}"
    )


ax.set_title(
    "Signal-to-Noise Ratio by Surface Condition",
    pad=14
)

ax.set_xlabel(
    "Surface condition"
)

ax.set_ylabel(
    "SNR (dB)"
)

ax.set_xticks(
    x
)

ax.set_xticklabels(
    SURFACE_ORDER
)

ax.legend(
    title="Hardness",
    frameon=True
)

ax.grid(
    axis="y",
    color=GRID_COLOR,
    alpha=0.60,
    linewidth=0.8
)

ax.set_axisbelow(True)

plt.tight_layout()


snr_figure = (
    SNR_FIGURE_FOLDER
    / "SNR_by_Surface_and_Hardness.png"
)

plt.savefig(
    snr_figure,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print(
    f"\nSaved SNR graph: "
    f"{snr_figure}"
)


# ============================================================
# 9. FINAL MESSAGE
# ============================================================

print("\n========================================")
print("MULTIMODAL ANALYSIS COMPLETE")
print("========================================")

print("\nΔR vs Force graphs:")

for hardness in HARDNESS_ORDER:
    print(
        f"  - H{hardness} ΔR vs Force "
        f"(full loading + unloading)"
    )

print(
    "  - SNR by Surface Condition"
)

print(
    f"\nFigures saved in:\n"
    f"{FIGURE_FOLDER}"
)