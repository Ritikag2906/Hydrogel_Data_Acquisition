"""
============================================================
HEATED HYDROGEL ELECTRICAL DATA ACQUISITION
============================================================

Author: Ritika Gupta
Institute: Max Planck Institute for Intelligent Systems

Project:
Smart Soft Sensor Architectures for Multimodal Perception

Purpose:
    Record the electrical response of the hydrogel while it
    is being heated.

Measurements:
    - Voltage (V)       -> Arduino
    - Resistance (Ohm)  -> Arduino
    - Time (s)          -> Python

Arduino:
    Port     = COM24
    Baudrate = 115200

Expected Arduino serial format:
    Voltage,Resistance

Example:
    1.203,39210.50

IMPORTANT:
    Close the Arduino Serial Monitor/Serial Plotter before
    running this Python script, otherwise COM24 may be busy.
"""

import os
import csv
import time
from datetime import datetime

import serial
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_DIR = (
    r"C:\Users\rgupta\Desktop\Master thesis"
    r"\Hydrogel_Data_Acquisition"
)

DATASET_DIR = (
    r"C:\Users\rgupta\Desktop\Master thesis"
    r"\Hydrogel_Data_Acquisition\Dataset"
)

FIGURES_DIR = (
    r"C:\Users\rgupta\Desktop\Master thesis"
    r"\Hydrogel_Data_Acquisition\Figures"
)


# ============================================================
# 2. HEATED HYDROGEL FOLDERS
# ============================================================

HEATED_DATASET_DIR = os.path.join(
    DATASET_DIR,
    "Heated_Hydrogel"
)

HEATED_FIGURES_DIR = os.path.join(
    FIGURES_DIR,
    "Heated_Hydrogel"
)

os.makedirs(HEATED_DATASET_DIR, exist_ok=True)
os.makedirs(HEATED_FIGURES_DIR, exist_ok=True)


# ============================================================
# 3. ARDUINO SETTINGS
# ============================================================

PORT = "COM24"
BAUDRATE = 115200
SERIAL_TIMEOUT = 1


# ============================================================
# 4. AUTOMATIC EXPERIMENT NUMBER
# ============================================================

def get_next_experiment_number(folder):
    existing_files = os.listdir(folder)
    numbers = []

    for filename in existing_files:
        if (
            filename.startswith("Heated_Hydrogel_")
            and filename.endswith(".csv")
        ):
            name = filename.replace(
                "Heated_Hydrogel_", ""
            )
            name = name.replace(".csv", "")

            try:
                number = int(name)
                numbers.append(number)
            except ValueError:
                pass

    if len(numbers) == 0:
        return 1

    return max(numbers) + 1


experiment_number = get_next_experiment_number(
    HEATED_DATASET_DIR
)

experiment_id = (
    f"Heated_Hydrogel_{experiment_number:02d}"
)


# ============================================================
# 5. FILE PATHS
# ============================================================

filepath = os.path.join(
    HEATED_DATASET_DIR,
    f"{experiment_id}.csv"
)

figure_path = os.path.join(
    HEATED_FIGURES_DIR,
    f"{experiment_id}.png"
)

metadata_path = os.path.join(
    HEATED_DATASET_DIR,
    "metadata.csv"
)


# ============================================================
# 6. EXPERIMENT INFORMATION
# ============================================================

print("\n" + "=" * 65)
print("HEATED HYDROGEL")
print("ELECTRICAL DATA ACQUISITION")
print("=" * 65)

print("\nExperiment:")
print(f"  {experiment_id}")

heating_method = input(
    "\nHeating method: "
).strip()

if heating_method == "":
    heating_method = "Not specified"

notes = input(
    "Notes (optional): "
).strip()


# ============================================================
# 7. DISPLAY STORAGE INFORMATION
# ============================================================

print("\n" + "-" * 65)
print("Storage")
print("-" * 65)

print("\nDataset:")
print(filepath)

print("\nFigure:")
print(figure_path)


# ============================================================
# 8. CONNECT TO ARDUINO
# ============================================================

print("\nConnecting to Arduino...")

ser = None
outputfile = None
acquisition_start_datetime = None

try:
    ser = serial.Serial(
        PORT,
        BAUDRATE,
        timeout=SERIAL_TIMEOUT
    )

    # Allow Arduino to reset after opening serial.
    time.sleep(2)

    # Remove old serial data.
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    print("Arduino connected successfully!")

    # ========================================================
    # 9. CREATE CSV
    # ========================================================

    outputfile = open(
        filepath,
        "w",
        newline=""
    )

    writer = csv.writer(outputfile)

    writer.writerow([
        "Time (s)",
        "Voltage (V)",
        "Resistance (Ohm)"
    ])

    print("CSV file created.")

    # ========================================================
    # 10. PREPARE EXPERIMENT
    # ========================================================

    print("\n" + "=" * 65)
    print("READY FOR HEATING EXPERIMENT")
    print("=" * 65)

    print("\nMake sure:")
    print("  1. Hydrogel is positioned correctly.")
    print("  2. Electrical connections are ready.")
    print("  3. Heating system is ready.")

    print("\nIMPORTANT:")
    print("Press ENTER to start data acquisition.")
    print("Start heating immediately after ENTER.")
    print("Press Ctrl + C when the experiment is finished.")

    input("\nPress ENTER to start acquisition...")

    # ========================================================
    # 11. START ACQUISITION
    # ========================================================

    acquisition_start_datetime = datetime.now().isoformat(
        timespec="milliseconds"
    )

    start_time = time.perf_counter()
    print_time = start_time

    print("\n" + "-" * 65)
    print("ACQUISITION STARTED")
    print("-" * 65)

    print(f"Experiment: {experiment_id}")
    print(f"Start time: {acquisition_start_datetime}")
    print("\nRecording:")
    print("Voltage + Resistance")
    print("\nStart heating now.")
    print("The first valid electrical reading will be used as the baseline.")
    print("Press Ctrl + C to stop.\n")

    # ========================================================
    # 12. DATA ACQUISITION
    # ========================================================

    while True:
        try:
            line = (
                ser.readline()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
                .strip()
            )

            if not line:
                continue

            # Expected:
            # Voltage,Resistance
            data = line.split(",")

            if len(data) != 2:
                continue

            try:
                voltage = float(data[0].strip())
                resistance = float(data[1].strip())
            except ValueError:
                continue

            # Ignore invalid electrical readings.
            # During Arduino startup, the voltage-divider calculation
            # can briefly produce negative resistance values when the
            # measured voltage is very close to the supply voltage.
            # These values are not physically meaningful and should
            # not be included in the heated-hydrogel dataset.
            if not np.isfinite(voltage) or not np.isfinite(resistance):
                continue

            if resistance <= 0:
                continue

            elapsed_time = (
                time.perf_counter() - start_time
            )

            # Save data
            writer.writerow([
                elapsed_time,
                voltage,
                resistance
            ])

            outputfile.flush()

            # Console output once per second
            current_time = time.perf_counter()

            if current_time - print_time >= 1:
                print(
                    f"Time: {elapsed_time:8.2f} s | "
                    f"Voltage: {voltage:8.3f} V | "
                    f"Resistance: {resistance:10.2f} Ohm"
                )

                print_time = current_time

        except UnicodeDecodeError:
            continue


# ============================================================
# 13. STOPPING
# ============================================================

except KeyboardInterrupt:
    print("\n")
    print("Stopping acquisition...")

except serial.SerialException as error:
    print(
        "\nERROR: Could not communicate "
        "with Arduino."
    )
    print(f"Details: {error}")

finally:
    # Close Arduino
    if ser is not None and ser.is_open:
        ser.close()
        print("Arduino disconnected.")

    # Close CSV
    if outputfile is not None:
        outputfile.close()
        print("CSV file closed.")


# ============================================================
# 14. CHECK DATA
# ============================================================

if not os.path.exists(filepath):
    print("\nNo data file was created.")
    raise SystemExit

try:
    raw_data = np.genfromtxt(
        filepath,
        delimiter=",",
        skip_header=1
    )
except Exception as error:
    print(f"\nCould not read recorded data: {error}")
    raise SystemExit

if raw_data.size == 0:
    print("\nNo data was recorded.")
    print(
        "Check that the Arduino is sending "
        "Voltage,Resistance."
    )
    raise SystemExit

if raw_data.ndim == 1:
    raw_data = raw_data.reshape(1, -1)


# ============================================================
# 15. EXTRACT DATA
# ============================================================

time_data = raw_data[:, 0]
voltage_data = raw_data[:, 1]
resistance_data = raw_data[:, 2]


# ============================================================
# 16. EXPERIMENT SUMMARY VALUES
# ============================================================

duration = time_data[-1]
samples = len(raw_data)

if duration > 0:
    sampling_rate = samples / duration
else:
    sampling_rate = 0

initial_voltage = voltage_data[0]
final_voltage = voltage_data[-1]

initial_resistance = resistance_data[0]
final_resistance = resistance_data[-1]

minimum_voltage = np.nanmin(voltage_data)
maximum_voltage = np.nanmax(voltage_data)

minimum_resistance = np.nanmin(resistance_data)
maximum_resistance = np.nanmax(resistance_data)

delta_resistance = final_resistance - initial_resistance

if initial_resistance != 0:
    relative_resistance_change = (
        delta_resistance / initial_resistance
    ) * 100
else:
    relative_resistance_change = np.nan

delta_voltage = final_voltage - initial_voltage

if initial_voltage != 0:
    relative_voltage_change = (
        delta_voltage / initial_voltage
    ) * 100
else:
    relative_voltage_change = np.nan


# ============================================================
# 17. SAVE METADATA
# ============================================================

metadata_exists = os.path.exists(metadata_path)

with open(
    metadata_path,
    "a",
    newline=""
) as metadata_file:

    metadata_writer = csv.writer(metadata_file)

    if not metadata_exists:
        metadata_writer.writerow([
            "Experiment",
            "Experiment Type",
            "Heating Method",
            "Initial Voltage (V)",
            "Final Voltage (V)",
            "Minimum Voltage (V)",
            "Maximum Voltage (V)",
            "Initial Resistance (Ohm)",
            "Final Resistance (Ohm)",
            "Minimum Resistance (Ohm)",
            "Maximum Resistance (Ohm)",
            "Delta Voltage (V)",
            "Relative Voltage Change (%)",
            "Delta Resistance (Ohm)",
            "Relative Resistance Change (%)",
            "Duration (s)",
            "Sampling Rate (Hz)",
            "Start Time",
            "Notes"
        ])

    metadata_writer.writerow([
        experiment_id,
        "Heated Hydrogel",
        heating_method,
        initial_voltage,
        final_voltage,
        minimum_voltage,
        maximum_voltage,
        initial_resistance,
        final_resistance,
        minimum_resistance,
        maximum_resistance,
        delta_voltage,
        relative_voltage_change,
        delta_resistance,
        relative_resistance_change,
        duration,
        sampling_rate,
        acquisition_start_datetime,
        notes
    ])


# ============================================================
# 18. CREATE FIGURES
# ============================================================

fig, axes = plt.subplots(
    3,
    1,
    figsize=(11, 10)
)

# ------------------------------------------------------------
# Voltage vs Time
# ------------------------------------------------------------

axes[0].plot(
    time_data,
    voltage_data,
    linewidth=1.5
)

axes[0].set_title(
    f"{experiment_id} - Voltage During Heating"
)

axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Voltage (V)")
axes[0].grid(True, alpha=0.3)


# ------------------------------------------------------------
# Resistance vs Time
# ------------------------------------------------------------

axes[1].plot(
    time_data,
    resistance_data,
    linewidth=1.5
)

axes[1].set_title(
    f"{experiment_id} - Resistance During Heating"
)

axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Resistance (Ohm)")
axes[1].grid(True, alpha=0.3)


# ------------------------------------------------------------
# Resistance vs Voltage
# ------------------------------------------------------------

axes[2].plot(
    voltage_data,
    resistance_data,
    linewidth=1.5
)

axes[2].set_title(
    f"{experiment_id} - Resistance vs Voltage"
)

axes[2].set_xlabel("Voltage (V)")
axes[2].set_ylabel("Resistance (Ohm)")
axes[2].grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    figure_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 19. PRINT EXPERIMENT SUMMARY
# ============================================================

print("\n" + "=" * 65)
print("EXPERIMENT SUMMARY")
print("=" * 65)

print(f"Experiment           : {experiment_id}")
print(f"Heating method       : {heating_method}")
print(f"Duration             : {duration:.2f} s")
print(f"Samples              : {samples}")
print(f"Sampling rate        : {sampling_rate:.2f} Hz")

print("\nVoltage")
print(
    f"  Initial            : "
    f"{initial_voltage:.3f} V"
)
print(
    f"  Final              : "
    f"{final_voltage:.3f} V"
)
print(
    f"  Change             : "
    f"{delta_voltage:.3f} V"
)
print(
    f"  Relative change    : "
    f"{relative_voltage_change:.2f} %"
)
print(
    f"  Minimum            : "
    f"{minimum_voltage:.3f} V"
)
print(
    f"  Maximum            : "
    f"{maximum_voltage:.3f} V"
)

print("\nResistance")
print(
    f"  Initial            : "
    f"{initial_resistance:.2f} Ohm"
)
print(
    f"  Final              : "
    f"{final_resistance:.2f} Ohm"
)
print(
    f"  Change             : "
    f"{delta_resistance:.2f} Ohm"
)
print(
    f"  Relative change    : "
    f"{relative_resistance_change:.2f} %"
)
print(
    f"  Minimum            : "
    f"{minimum_resistance:.2f} Ohm"
)
print(
    f"  Maximum            : "
    f"{maximum_resistance:.2f} Ohm"
)

print("\n" + "-" * 65)
print("FILES")
print("-" * 65)

print("\nData:")
print(filepath)

print("\nMetadata:")
print(metadata_path)

print("\nFigure:")
print(figure_path)

print("\n" + "=" * 65)
print("EXPERIMENT COMPLETED SUCCESSFULLY!")
print("=" * 65)
