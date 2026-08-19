"""
------------------------------------------------------
Hydrogel Sensor Data Acquisition Software

Author : Ritika Gupta
Institute : Max Planck Institute for Intelligent Systems

Project:
Smart Soft Sensor Architectures for Multimodal Perception

Description:
Acquires voltage and resistance data from an Arduino,
saves datasets automatically, generates plots, and stores
experiment metadata for later multimodal data analysis.

Current measurements:
- Voltage
- Resistance

Mechanical measurements such as force, displacement,
strain, and stress are acquired separately using the
Instron system and will be synchronized later.
------------------------------------------------------
"""

import os
import csv
import time
from datetime import datetime

import serial
import numpy as np
import matplotlib.pyplot as plt


# ------------------------------------------------------
# Helper Functions
# ------------------------------------------------------

def is_float(element):
    """Check whether a string can be converted to float."""
    try:
        float(element)
        return True
    except ValueError:
        return False


# ------------------------------------------------------
# Folder Setup
# ------------------------------------------------------

testbeds = [
    "Baseline",
    "TB1",
    "TB2",
    "TB3",
    "TB4",
    "TB5"
]

# Create main dataset folder
os.makedirs("Dataset", exist_ok=True)

# Create dataset folders
for testbed in testbeds:
    os.makedirs(
        os.path.join("Dataset", testbed),
        exist_ok=True
    )

# Create main figure folder
os.makedirs("Figures", exist_ok=True)

# Create figure folders
for testbed in testbeds:
    os.makedirs(
        os.path.join("Figures", testbed),
        exist_ok=True
    )


# ------------------------------------------------------
# Program Start
# ------------------------------------------------------

print("=" * 55)
print("Hydrogel Sensor Data Acquisition")
print("=" * 55)


# ------------------------------------------------------
# Select Testbed
# ------------------------------------------------------

print("\nSelect Testbed")
print("1. Baseline (No Testbed)")
print("2. Testbed 1")
print("3. Testbed 2")
print("4. Testbed 3")
print("5. Testbed 4")
print("6. Testbed 5")

while True:

    choice = input("\nEnter choice (1-6): ").strip()

    if choice == "1":
        testbed = "Baseline"
        break

    elif choice == "2":
        testbed = "TB1"
        break

    elif choice == "3":
        testbed = "TB2"
        break

    elif choice == "4":
        testbed = "TB3"
        break

    elif choice == "5":
        testbed = "TB4"
        break

    elif choice == "6":
        testbed = "TB5"
        break

    else:
        print(
            "Invalid selection. "
            "Please choose 1, 2, 3, 4, 5, or 6."
        )


# ------------------------------------------------------
# Experiment Information
# ------------------------------------------------------

trial = input("Trial Number: ").strip()

hydrogel_batch = input(
    "Hydrogel Batch ID: "
).strip()

sensor_id = input(
    "Sensor ID: "
).strip()

notes = input(
    "Notes (optional): "
).strip()


# ------------------------------------------------------
# Create Trial ID
# ------------------------------------------------------

trial_id = f"{testbed}_T{trial}"

start_datetime = datetime.now().isoformat(
    timespec="seconds"
)

filename = f"{trial_id}.csv"

filepath = os.path.join(
    "Dataset",
    testbed,
    filename
)

print("\n" + "-" * 55)
print("Experiment Information")
print("-" * 55)

print(f"Trial ID       : {trial_id}")
print(f"Testbed        : {testbed}")
print(f"Hydrogel Batch : {hydrogel_batch}")
print(f"Sensor ID      : {sensor_id}")
print(f"Start Time     : {start_datetime}")

print("\nData will be saved to:")
print(filepath)


# ------------------------------------------------------
# Save Metadata
# ------------------------------------------------------

metadata_path = os.path.join(
    "Dataset",
    "metadata.csv"
)

metadata_exists = os.path.exists(metadata_path)

metadata_file = open(
    metadata_path,
    "a",
    newline=""
)

metadata_writer = csv.writer(metadata_file)

# Write header only when metadata.csv is created
if not metadata_exists:

    metadata_writer.writerow([
        "Trial ID",
        "Testbed",
        "Trial Number",
        "Hydrogel Batch",
        "Sensor ID",
        "Start Time",
        "Notes"
    ])

metadata_writer.writerow([
    trial_id,
    testbed,
    trial,
    hydrogel_batch,
    sensor_id,
    start_datetime,
    notes
])

metadata_file.flush()
metadata_file.close()


# ------------------------------------------------------
# Arduino Configuration
# ------------------------------------------------------

PORT = "COM24"
BAUDRATE = 115200

print("\nConnecting to Arduino...")


ser = None
outputfile = None


try:

    # --------------------------------------------------
    # Connect to Arduino
    # --------------------------------------------------

    ser = serial.Serial(
        PORT,
        BAUDRATE,
        timeout=1
    )

    time.sleep(2)

    print("Arduino connected successfully!")


    # --------------------------------------------------
    # Initialize Arduino
    # --------------------------------------------------

    ser.read(19)

    ser.reset_input_buffer()
    ser.reset_output_buffer()

    time.sleep(0.5)

    print("Arduino initialized.")


    # --------------------------------------------------
    # Create CSV File
    # --------------------------------------------------

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


    # --------------------------------------------------
    # Initialize Data Acquisition
    # --------------------------------------------------

    dataADC = [
        0.0,
        0.0
    ]

    startTime = time.time()
    printTime = time.time()

    print("\n" + "=" * 55)
    print("Starting data acquisition...")
    print("=" * 55)

    print("Press Ctrl + C to stop.\n")


    # --------------------------------------------------
    # Data Acquisition Loop
    # --------------------------------------------------

    while True:

        try:

            line = (
                ser.readline()
                .decode("utf-8")
                .strip()
            )

            # Skip empty lines
            if not line:
                continue


            # --------------------------------------------------
            # Parse Arduino Data
            # --------------------------------------------------

            dataADC_ = line.split(",")


            if (
                len(dataADC_) == 2
                and is_float(dataADC_[0])
                and is_float(dataADC_[1])
            ):

                voltage = float(
                    dataADC_[0]
                )

                resistance = float(
                    dataADC_[1]
                )

                elapsed_time = (
                    time.time() - startTime
                )


                # --------------------------------------------------
                # Save Data
                # --------------------------------------------------

                writer.writerow([
                    elapsed_time,
                    voltage,
                    resistance
                ])

                # Flush data to disk
                outputfile.flush()


                # Update latest values
                dataADC[0] = voltage
                dataADC[1] = resistance


            # --------------------------------------------------
            # Print Status Every Second
            # --------------------------------------------------

            if (
                time.time() - printTime
            ) >= 1:

                print(
                    f"Time: {elapsed_time:7.2f} s | "
                    f"Voltage: {dataADC[0]:7.3f} V | "
                    f"Resistance: {dataADC[1]:10.2f} Ω"
                )

                printTime = time.time()


        except UnicodeDecodeError:

            # Ignore corrupted serial characters
            continue


# ------------------------------------------------------
# Stop Acquisition
# ------------------------------------------------------

except KeyboardInterrupt:

    print("\n\nStopping acquisition...")


# ------------------------------------------------------
# Serial Connection Error
# ------------------------------------------------------

except serial.SerialException as error:

    print("\nERROR: Could not communicate with Arduino.")

    print(f"Details: {error}")

    raise


# ------------------------------------------------------
# General Error
# ------------------------------------------------------

except Exception as error:

    print("\nUnexpected error occurred.")

    print(f"Details: {error}")

    raise


# ------------------------------------------------------
# Finalize Experiment
# ------------------------------------------------------

finally:

    # --------------------------------------------------
    # Close Arduino
    # --------------------------------------------------

    if ser is not None and ser.is_open:

        ser.close()

        print("Arduino disconnected.")


    # --------------------------------------------------
    # Close CSV
    # --------------------------------------------------

    if outputfile is not None:

        outputfile.close()

        print("CSV file closed.")


# ------------------------------------------------------
# Check Whether Data Was Recorded
# ------------------------------------------------------

if not os.path.exists(filepath):

    print("\nNo data file was created.")

    raise SystemExit


# ------------------------------------------------------
# Load Recorded Data
# ------------------------------------------------------

rawData = np.genfromtxt(
    filepath,
    delimiter=",",
    skip_header=1
)


# Check whether data exists
if rawData.size == 0:

    print("No data was recorded.")

    raise SystemExit


# If only one sample exists
if rawData.ndim == 1:

    rawData = rawData.reshape(
        1,
        -1
    )


# ------------------------------------------------------
# Create Figure
# ------------------------------------------------------

figure_path = os.path.join(
    "Figures",
    testbed,
    f"{trial_id}.png"
)


fig, (
    ax1,
    ax2
) = plt.subplots(
    2,
    1,
    figsize=(10, 8),
    sharex=True
)


# ------------------------------------------------------
# Voltage Plot
# ------------------------------------------------------

ax1.plot(
    rawData[:, 0],
    rawData[:, 1],
    linewidth=1.5
)

ax1.set_title(
    f"{testbed} — Trial {trial}"
)

ax1.set_ylabel(
    "Voltage (V)"
)

ax1.set_ylim(
    [-0.2, 5.2]
)

ax1.grid(
    True,
    alpha=0.3
)


# ------------------------------------------------------
# Resistance Plot
# ------------------------------------------------------

ymin = (
    np.min(rawData[:, 2])
    - 250
)

ymax = (
    np.max(rawData[:, 2])
    + 250
)

ax2.plot(
    rawData[:, 0],
    rawData[:, 2],
    linewidth=1.5
)

ax2.set_xlabel(
    "Time (s)"
)

ax2.set_ylabel(
    "Resistance (Ω)"
)

ax2.set_ylim(
    [ymin, ymax]
)

ax2.grid(
    True,
    alpha=0.3
)


# ------------------------------------------------------
# Save Figure
# ------------------------------------------------------

plt.tight_layout()

plt.savefig(
    figure_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ------------------------------------------------------
# Experiment Summary
# ------------------------------------------------------

duration = rawData[-1, 0]

samples = len(rawData)

if duration > 0:

    sampling_rate = (
        samples / duration
    )

else:

    sampling_rate = 0


print("\n" + "=" * 55)
print("Experiment Summary")
print("=" * 55)

print(
    f"Trial ID       : {trial_id}"
)

print(
    f"Testbed        : {testbed}"
)

print(
    f"Hydrogel Batch : {hydrogel_batch}"
)

print(
    f"Sensor ID      : {sensor_id}"
)

print(
    f"Duration       : {duration:.2f} s"
)

print(
    f"Samples        : {samples}"
)

print(
    f"Sampling Rate  : {sampling_rate:.2f} Hz"
)


# ------------------------------------------------------
# Voltage Statistics
# ------------------------------------------------------

print("\nVoltage")

print(
    f"  Min          : "
    f"{np.min(rawData[:, 1]):.3f} V"
)

print(
    f"  Max          : "
    f"{np.max(rawData[:, 1]):.3f} V"
)

print(
    f"  Mean         : "
    f"{np.mean(rawData[:, 1]):.3f} V"
)


# ------------------------------------------------------
# Resistance Statistics
# ------------------------------------------------------

print("\nResistance")

print(
    f"  Min          : "
    f"{np.min(rawData[:, 2]):.2f} Ω"
)

print(
    f"  Max          : "
    f"{np.max(rawData[:, 2]):.2f} Ω"
)

print(
    f"  Mean         : "
    f"{np.mean(rawData[:, 2]):.2f} Ω"
)


# ------------------------------------------------------
# File Locations
# ------------------------------------------------------

print("\nData saved to:")
print(filepath)

print("\nMetadata saved to:")
print(metadata_path)

print("\nFigure saved to:")
print(figure_path)

print("\nExperiment completed successfully!")