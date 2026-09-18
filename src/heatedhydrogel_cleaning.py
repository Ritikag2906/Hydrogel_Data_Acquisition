"""
TEMPORARY CLEANING SCRIPT FOR HEATED HYDROGEL DATA

Purpose:
    Remove physically invalid resistance readings (<= 0 Ohm)
    from already-recorded Heated_Hydrogel CSV files.

IMPORTANT:
    - Original CSV files are NOT modified.
    - Cleaned files are saved with "_cleaned" in the filename.
    - Run this after your existing experiments.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. FOLDER
# ============================================================

DATASET_DIR = (
    r"C:\Users\rgupta\Desktop\Master thesis"
    r"\Hydrogel_Data_Acquisition\Dataset"
    r"\Heated_Hydrogel"
)

FIGURES_DIR = (
    r"C:\Users\rgupta\Desktop\Master thesis"
    r"\Hydrogel_Data_Acquisition\Figures"
    r"\Heated_Hydrogel"
)

os.makedirs(FIGURES_DIR, exist_ok=True)


# ============================================================
# 2. FIND ORIGINAL EXPERIMENT FILES
# ============================================================

files = sorted(
    filename
    for filename in os.listdir(DATASET_DIR)
    if (
        filename.startswith("Heated_Hydrogel_")
        and filename.endswith(".csv")
        and "_cleaned" not in filename
    )
)

if not files:
    print("No Heated_Hydrogel CSV files found.")
    raise SystemExit

print("=" * 65)
print("HEATED HYDROGEL - TEMPORARY DATA CLEANING")
print("=" * 65)

print("\nFiles found:")
for filename in files:
    print("  ", filename)


# ============================================================
# 3. PROCESS EACH FILE
# ============================================================

for filename in files:

    input_path = os.path.join(
        DATASET_DIR,
        filename
    )

    base_name = filename.replace(
        ".csv",
        ""
    )

    cleaned_filename = (
        base_name + "_cleaned.csv"
    )

    cleaned_path = os.path.join(
        DATASET_DIR,
        cleaned_filename
    )

    figure_filename = (
        base_name + "_cleaned.png"
    )

    figure_path = os.path.join(
        FIGURES_DIR,
        figure_filename
    )

    print("\n" + "-" * 65)
    print(f"Processing: {filename}")
    print("-" * 65)

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    data = np.genfromtxt(
        input_path,
        delimiter=",",
        skip_header=1
    )

    if data.size == 0:
        print("No data found. Skipping.")
        continue

    if data.ndim == 1:
        data = data.reshape(1, -1)

    if data.shape[1] < 3:
        print("CSV does not contain the expected 3 columns.")
        continue

    # --------------------------------------------------------
    # Extract columns
    # --------------------------------------------------------

    time_data = data[:, 0]
    voltage_data = data[:, 1]
    resistance_data = data[:, 2]

    original_samples = len(data)

    # --------------------------------------------------------
    # Remove invalid values
    #
    # Only remove:
    #   - negative resistance
    #   - zero resistance
    #   - NaN / infinite resistance
    #
    # Voltage is kept as recorded.
    # --------------------------------------------------------

    valid = (
        np.isfinite(time_data)
        & np.isfinite(voltage_data)
        & np.isfinite(resistance_data)
        & (resistance_data > 0)
    )

    cleaned_data = data[valid]

    removed_samples = (
        original_samples - len(cleaned_data)
    )

    print(f"Original samples : {original_samples}")
    print(f"Removed samples  : {removed_samples}")
    print(f"Valid samples    : {len(cleaned_data)}")

    if len(cleaned_data) == 0:
        print("No valid samples remain. Skipping.")
        continue

    # --------------------------------------------------------
    # Save cleaned CSV
    # --------------------------------------------------------

    with open(
        cleaned_path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Time (s)",
            "Voltage (V)",
            "Resistance (Ohm)"
        ])

        writer.writerows(
            cleaned_data.tolist()
        )

    print("\nCleaned CSV saved:")
    print(cleaned_path)

    # --------------------------------------------------------
    # Recalculate values using first VALID reading
    # --------------------------------------------------------

    clean_time = cleaned_data[:, 0]
    clean_voltage = cleaned_data[:, 1]
    clean_resistance = cleaned_data[:, 2]

    initial_voltage = clean_voltage[0]
    final_voltage = clean_voltage[-1]

    initial_resistance = clean_resistance[0]
    final_resistance = clean_resistance[-1]

    delta_voltage = (
        final_voltage - initial_voltage
    )

    delta_resistance = (
        final_resistance - initial_resistance
    )

    if initial_voltage != 0:
        voltage_change_percent = (
            delta_voltage / initial_voltage
        ) * 100
    else:
        voltage_change_percent = np.nan

    if initial_resistance != 0:
        resistance_change_percent = (
            delta_resistance / initial_resistance
        ) * 100
    else:
        resistance_change_percent = np.nan

    print("\nCleaned experiment:")
    print(
        f"Initial voltage    : "
        f"{initial_voltage:.3f} V"
    )
    print(
        f"Final voltage      : "
        f"{final_voltage:.3f} V"
    )
    print(
        f"Voltage change     : "
        f"{voltage_change_percent:.2f} %"
    )

    print(
        f"Initial resistance : "
        f"{initial_resistance:.2f} Ohm"
    )
    print(
        f"Final resistance   : "
        f"{final_resistance:.2f} Ohm"
    )
    print(
        f"Resistance change  : "
        f"{resistance_change_percent:.2f} %"
    )

    # --------------------------------------------------------
    # Create cleaned plots
    # --------------------------------------------------------

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(11, 8)
    )

    axes[0].plot(
        clean_time,
        clean_voltage,
        linewidth=1.5
    )

    axes[0].set_title(
        f"{base_name} - Voltage During Heating"
    )
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Voltage (V)")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(
        clean_time,
        clean_resistance,
        linewidth=1.5
    )

    axes[1].set_title(
        f"{base_name} - Resistance During Heating"
    )
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Resistance (Ohm)")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print("\nCleaned figure saved:")
    print(figure_path)


# ============================================================
# 4. FINISHED
# ============================================================

print("\n" + "=" * 65)
print("CLEANING COMPLETED")
print("=" * 65)

print("\nYour original CSV files were NOT changed.")
print("New files have '_cleaned' added to their names.")
print("\nYou can now compare the cleaned datasets.")
