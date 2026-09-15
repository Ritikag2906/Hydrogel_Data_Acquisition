"""
Arduino + Instron Synchronization - All Main Trials

Author: Ritika Gupta
Institute: Max Planck Institute for Intelligent Systems

Project:
Smart Soft Sensor Architectures for Multimodal Perception

Purpose:
Synchronize the Arduino electrical measurements with the Instron
mechanical measurements for all main experimental conditions.

The Arduino time is used as the common time base.
The Instron time is shifted so that the beginning of mechanical
loading is used as the synchronization reference.

The raw resistance signal is kept unchanged.
A lightly smoothed resistance signal is added as an additional
column for later analysis.

Main conditions:
    Smooth: H10, H20, H30, H50
    Rough:  H10/H20/H30/H50 with R30 and R40
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

ARDUINO_DIR = os.path.join(
    PROJECT_DIR,
    "Dataset",
    "Arduino_Instron_Data"
)

INSTRON_DIR = os.path.join(
    PROJECT_DIR,
    "Dataset",
    "Instron_Data"
)

OUTPUT_DIR = os.path.join(
    PROJECT_DIR,
    "Analysis",
    "Synchronized_Data"
)

FIGURES_DIR = os.path.join(
    PROJECT_DIR,
    "Figures",
    "Synchronization",
    "All_Trials"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


# ======================================================
# ANALYSIS SETTINGS
# ======================================================

# Keep the raw resistance signal.
# The smoothed signal is only added as another column.

APPLY_SMOOTHING = True

# At approximately 83 Hz, 11 samples correspond to about
# 0.13 seconds.

SMOOTHING_WINDOW = 11

# Small increase above the initial force baseline used
# to detect the beginning of mechanical loading.

FORCE_ONSET_MARGIN = 0.005

# Force must stay above the threshold for this duration
# to avoid detecting a single noisy point.

MIN_SUSTAINED_LOADING_TIME = 0.15


# ======================================================
# EXPERIMENTAL CONDITIONS
# ======================================================

conditions = [
    ("Smooth", 10),
    ("Smooth", 20),
    ("Smooth", 30),
    ("Smooth", 50),

    ("R30", 10),
    ("R40", 10),

    ("R30", 20),
    ("R40", 20),

    ("R30", 30),
    ("R40", 30),

    ("R30", 50),
    ("R40", 50),
]


# ======================================================
# FIND ARDUINO FILE
# ======================================================

def find_arduino_file(surface, hardness):
    """
    Find the Arduino CSV for one experimental condition.

    For smooth samples, Trial 01 is selected because there are
    two smooth Arduino recordings for each hardness.
    """

    if surface == "Smooth":

        folder = os.path.join(
            ARDUINO_DIR,
            "SmoothSurface",
            f"Hardness_{hardness}"
        )

        files = glob.glob(
            os.path.join(folder, "*.csv")
        )

        if len(files) == 0:
            return None

        trial_01 = [
            file for file in files
            if "T01" in os.path.basename(file)
        ]

        if len(trial_01) > 0:
            return trial_01[0]

        return files[0]

    else:

        folder = os.path.join(
            ARDUINO_DIR,
            "RoughSurface",
            f"Rough_H{hardness}_{surface}"
        )

        files = glob.glob(
            os.path.join(folder, "*.csv")
        )

        if len(files) == 0:
            return None

        return files[0]


# ======================================================
# FIND INSTRON FILE
# ======================================================

def find_instron_file(surface, hardness):
    """
    Find the Instron CSV for one experimental condition.
    """

    if surface == "Smooth":

        folder_pattern = os.path.join(
            INSTRON_DIR,
            "SmoothSurface",
            f"Hardness_{hardness}_Trial01.is_ccyclic_Exports*"
        )

    else:

        roughness = surface.replace("R", "")

        folder_pattern = os.path.join(
            INSTRON_DIR,
            "RoughSurface",
            f"Hardness_{hardness}_Trialden{roughness}.is_ccyclic_Exports*"
        )

    folders = glob.glob(folder_pattern)

    if len(folders) == 0:
        return None

    csv_files = glob.glob(
        os.path.join(
            folders[0],
            "*.csv"
        )
    )

    if len(csv_files) == 0:
        return None

    return csv_files[0]


# ======================================================
# READ AND PREPARE ARDUINO DATA
# ======================================================

def read_arduino(file_path):

    arduino = pd.read_csv(file_path)

    columns = [
        "Time (s)",
        "Voltage (V)",
        "Resistance (Ohm)"
    ]

    for column in columns:
        if column not in arduino.columns:
            raise ValueError(
                f"Missing Arduino column: {column}"
            )

    arduino = arduino[columns].copy()

    for column in columns:
        arduino[column] = pd.to_numeric(
            arduino[column],
            errors="coerce"
        )

    arduino = arduino.dropna()
    arduino = arduino.sort_values("Time (s)")
    arduino = arduino.drop_duplicates("Time (s)")
    arduino = arduino.reset_index(drop=True)

    return arduino


# ======================================================
# READ AND PREPARE INSTRON DATA
# ======================================================

def read_instron(file_path):

    instron = pd.read_csv(file_path)

    columns = [
        "Time",
        "Displacement",
        "Force",
        "Compressive strain (Displacement)",
        "Compressive stress"
    ]

    for column in columns:
        if column not in instron.columns:
            raise ValueError(
                f"Missing Instron column: {column}"
            )

    instron = instron[columns].copy()

    for column in columns:
        instron[column] = pd.to_numeric(
            instron[column],
            errors="coerce"
        )

    instron = instron.dropna()
    instron = instron.sort_values("Time")
    instron = instron.drop_duplicates("Time")
    instron = instron.reset_index(drop=True)

    return instron


# ======================================================
# DETECT MECHANICAL LOADING START
# ======================================================

def detect_loading_start(instron_time, force):

    initial_points = max(
        10,
        int(0.05 * len(force))
    )

    initial_force = np.median(
        force[:initial_points]
    )

    force_threshold = (
        initial_force +
        FORCE_ONSET_MARGIN
    )

    above_threshold = (
        force > force_threshold
    )

    time_step = np.median(
        np.diff(instron_time)
    )

    minimum_points = max(
        3,
        int(
            MIN_SUSTAINED_LOADING_TIME /
            time_step
        )
    )

    loading_start_index = None
    count = 0

    for i, value in enumerate(above_threshold):

        if value:
            count += 1
        else:
            count = 0

        if count >= minimum_points:

            loading_start_index = (
                i - minimum_points + 1
            )

            break

    if loading_start_index is None:

        print(
            "\nWarning: mechanical loading start "
            "could not be detected automatically."
        )

        print(
            "The beginning of the Instron recording "
            "will be used instead."
        )

        loading_start_index = 0

    loading_start = instron_time[
        loading_start_index
    ]

    return (
        loading_start,
        initial_force,
        force_threshold,
        loading_start_index
    )


# ======================================================
# PROCESS ONE TRIAL
# ======================================================

def synchronize_trial(surface, hardness):

    condition_name = (
        f"H{hardness}_{surface}"
    )

    print("\n----------------------------------------------")
    print(f"Processing: {condition_name}")
    print("----------------------------------------------")

    arduino_file = find_arduino_file(
        surface,
        hardness
    )

    instron_file = find_instron_file(
        surface,
        hardness
    )

    if arduino_file is None:
        print("Arduino file not found.")
        return None

    if instron_file is None:
        print("Instron file not found.")
        return None

    print(f"Arduino: {arduino_file}")
    print(f"Instron: {instron_file}")

    arduino = read_arduino(
        arduino_file
    )

    instron = read_instron(
        instron_file
    )

    # --------------------------------------------------
    # Reset both time axes
    # --------------------------------------------------

    arduino_time = (
        arduino["Time (s)"].to_numpy()
    )

    instron_time = (
        instron["Time"].to_numpy()
    )

    arduino_time = (
        arduino_time -
        arduino_time[0]
    )

    instron_time = (
        instron_time -
        instron_time[0]
    )

    # --------------------------------------------------
    # Detect loading onset
    # --------------------------------------------------

    force = instron["Force"].to_numpy()

    (
        instron_loading_start,
        initial_force,
        force_threshold,
        loading_start_index
    ) = detect_loading_start(
        instron_time,
        force
    )

    # --------------------------------------------------
    # Shift Instron time
    # --------------------------------------------------

    instron_aligned_time = (
        instron_time -
        instron_loading_start
    )

    # --------------------------------------------------
    # Find common time range
    # --------------------------------------------------

    time_start = max(
        np.min(arduino_time),
        np.min(instron_aligned_time)
    )

    time_end = min(
        np.max(arduino_time),
        np.max(instron_aligned_time)
    )

    common_mask = (
        (arduino_time >= time_start) &
        (arduino_time <= time_end)
    )

    common_time = arduino_time[
        common_mask
    ]

    if len(common_time) < 10:
        print(
            "Not enough overlapping data. "
            "Trial was skipped."
        )
        return None

    # --------------------------------------------------
    # Interpolate Instron data onto Arduino time
    # --------------------------------------------------

    displacement = np.interp(
        common_time,
        instron_aligned_time,
        instron["Displacement"].to_numpy()
    )

    force_sync = np.interp(
        common_time,
        instron_aligned_time,
        instron["Force"].to_numpy()
    )

    strain = np.interp(
        common_time,
        instron_aligned_time,
        instron[
            "Compressive strain (Displacement)"
        ].to_numpy()
    )

    stress = np.interp(
        common_time,
        instron_aligned_time,
        instron[
            "Compressive stress"
        ].to_numpy()
    )

    # --------------------------------------------------
    # Select Arduino data
    # --------------------------------------------------

    arduino_common = arduino.loc[
        common_mask
    ].reset_index(drop=True)

    # --------------------------------------------------
    # Create synchronized dataset
    # --------------------------------------------------

    synchronized = pd.DataFrame({

        "Time (s)": common_time,

        "Resistance (Ohm)": (
            arduino_common[
                "Resistance (Ohm)"
            ].to_numpy()
        ),

        "Voltage (V)": (
            arduino_common[
                "Voltage (V)"
            ].to_numpy()
        ),

        "Displacement": displacement,

        "Force (N)": force_sync,

        "Strain": strain,

        "Stress (MPa)": stress
    })

    # --------------------------------------------------
    # Add smoothed resistance
    # --------------------------------------------------

    if APPLY_SMOOTHING:

        synchronized[
            "Resistance Smoothed (Ohm)"
        ] = (
            synchronized[
                "Resistance (Ohm)"
            ]
            .rolling(
                window=SMOOTHING_WINDOW,
                center=True,
                min_periods=1
            )
            .median()
        )

    else:

        synchronized[
            "Resistance Smoothed (Ohm)"
        ] = synchronized[
            "Resistance (Ohm)"
        ]

    # --------------------------------------------------
    # Save synchronized data
    # --------------------------------------------------

    output_name = (
        f"Synchronized_{condition_name}_T01.csv"
    )

    output_file = os.path.join(
        OUTPUT_DIR,
        output_name
    )

    synchronized.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------
    # Sampling information
    # --------------------------------------------------

    arduino_sampling_rate = (
        1 /
        np.median(
            np.diff(common_time)
        )
    )

    instron_sampling_rate = (
        1 /
        np.median(
            np.diff(instron_time)
        )
    )

    synchronized_duration = (
        common_time[-1] -
        common_time[0]
    )

    # --------------------------------------------------
    # Print results
    # --------------------------------------------------

    print(
        f"\nLoading onset: "
        f"{instron_loading_start:.4f} s"
    )

    print(
        f"Force threshold: "
        f"{force_threshold:.6f} N"
    )

    print(
        f"Arduino sampling rate: "
        f"{arduino_sampling_rate:.2f} Hz"
    )

    print(
        f"Instron sampling rate: "
        f"{instron_sampling_rate:.2f} Hz"
    )

    print(
        f"Synchronized samples: "
        f"{len(synchronized)}"
    )

    print(
        f"Synchronized duration: "
        f"{synchronized_duration:.3f} s"
    )

    print(
        f"Saved to: {output_file}"
    )

    # --------------------------------------------------
    # Plot 1 - Loading onset
    # --------------------------------------------------

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        instron_time,
        force,
        linewidth=2,
        label="Instron force"
    )

    plt.axvline(
        instron_loading_start,
        linestyle="--",
        linewidth=1.8,
        label=(
            f"Loading onset "
            f"({instron_loading_start:.2f} s)"
        )
    )

    plt.xlabel(
        "Instron time (s)"
    )

    plt.ylabel(
        "Force (N)"
    )

    plt.title(
        f"Plot 1 - Mechanical Loading Onset: "
        f"H{hardness} {surface}"
    )

    plt.legend()
    plt.grid(
        True,
        alpha=0.25
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIGURES_DIR,
            f"01_Loading_Onset_H{hardness}_{surface}.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # --------------------------------------------------
    # Plot 2 - Synchronization check
    # --------------------------------------------------

    fig, ax1 = plt.subplots(
        figsize=(11, 6.5)
    )

    force_line, = ax1.plot(
        synchronized["Time (s)"],
        synchronized["Force (N)"],
        linewidth=2,
        label="Force"
    )

    ax1.set_xlabel(
        "Synchronized time (s)"
    )

    ax1.set_ylabel(
        "Force (N)"
    )

    ax2 = ax1.twinx()

    raw_line, = ax2.plot(
        synchronized["Time (s)"],
        synchronized["Resistance (Ohm)"],
        linewidth=0.7,
        alpha=0.25,
        label="Raw resistance"
    )

    smooth_line, = ax2.plot(
        synchronized["Time (s)"],
        synchronized[
            "Resistance Smoothed (Ohm)"
        ],
        linewidth=2,
        label="Smoothed resistance"
    )

    ax2.set_ylabel(
        "Resistance (Ohm)"
    )

    ax1.grid(
        True,
        alpha=0.25
    )

    lines = [
        force_line,
        raw_line,
        smooth_line
    ]

    labels = [
        line.get_label()
        for line in lines
    ]

    ax1.legend(
        lines,
        labels,
        loc="upper left"
    )

    plt.title(
        f"Plot 2 - Synchronization Check: "
        f"H{hardness} {surface}"
    )

    fig.tight_layout()

    plt.savefig(
        os.path.join(
            FIGURES_DIR,
            f"02_Synchronization_Check_H{hardness}_{surface}.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # --------------------------------------------------
    # Plot 3 - Resistance vs displacement
    # --------------------------------------------------

    plt.figure(
        figsize=(9, 6)
    )

    plt.plot(
        synchronized["Displacement"],
        synchronized[
            "Resistance Smoothed (Ohm)"
        ],
        linewidth=2
    )

    plt.xlabel(
        "Displacement"
    )

    plt.ylabel(
        "Resistance (Ohm)"
    )

    plt.title(
        f"Plot 3 - Resistance Response vs "
        f"Displacement: H{hardness} {surface}"
    )

    plt.grid(
        True,
        alpha=0.25
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIGURES_DIR,
            f"03_Resistance_vs_Displacement_H{hardness}_{surface}.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # --------------------------------------------------
    # Return summary information
    # --------------------------------------------------

    return {
        "Condition": condition_name,
        "Hardness": hardness,
        "Surface": surface,
        "Loading Onset (s)": instron_loading_start,
        "Initial Force (N)": initial_force,
        "Force Threshold (N)": force_threshold,
        "Arduino Sampling Rate (Hz)": arduino_sampling_rate,
        "Instron Sampling Rate (Hz)": instron_sampling_rate,
        "Synchronized Samples": len(synchronized),
        "Synchronized Duration (s)": synchronized_duration,
        "Arduino File": arduino_file,
        "Instron File": instron_file,
        "Output File": output_file
    }


# ======================================================
# RUN ALL CONDITIONS
# ======================================================

print("\n==============================================")
print("ARDUINO + INSTRON SYNCHRONIZATION")
print("ALL MAIN EXPERIMENTAL CONDITIONS")
print("==============================================")


results = []

for surface, hardness in conditions:

    try:

        result = synchronize_trial(
            surface,
            hardness
        )

        if result is not None:
            results.append(result)

    except Exception as error:

        print(
            f"\nError while processing "
            f"H{hardness} {surface}:"
        )

        print(error)


# ======================================================
# SAVE SUMMARY
# ======================================================

summary = pd.DataFrame(results)

summary_file = os.path.join(
    OUTPUT_DIR,
    "Synchronization_Summary.csv"
)

summary.to_csv(
    summary_file,
    index=False
)


# ======================================================
# FINAL OUTPUT
# ======================================================

print("\n==============================================")
print("SYNCHRONIZATION COMPLETED")
print("==============================================")

print(
    f"\nTrials successfully synchronized: "
    f"{len(results)} / {len(conditions)}"
)

print(
    f"\nSynchronized data saved to:"
    f"\n{OUTPUT_DIR}"
)

print(
    f"\nSummary saved to:"
    f"\n{summary_file}"
)

print(
    f"\nFigures saved to:"
    f"\n{FIGURES_DIR}"
)

print(
    "\nThe raw resistance signal was preserved."
)

print(
    "A smoothed resistance signal was added "
    "as a separate column."
)

print(
    "\nNext step: review the synchronization "
    "summary and plots before feature extraction."
)
