"""
------------------------------------------------------
Hydrogel Sensor Data Acquisition Software

Author : Ritika Gupta
Institute : Max Planck Institute for Intelligent Systems

Project:
Smart Soft Sensor Architectures for Multimodal Perception

Description:
Acquires voltage and resistance data from an Arduino,
saves datasets automatically, generates plots,
and prepares data for machine learning.
------------------------------------------------------
"""

import os
import csv
import time
from datetime import datetime

import serial
import numpy as np
import matplotlib.pyplot as plt


# Helper Functions

def is_float(element):
    """Checks whether a string can be converted to float."""
    try:
        float(element)
        return True
    except ValueError:
        return False

# Create folders automatically
os.makedirs("Dataset", exist_ok=True)
os.makedirs("Dataset/Baseline", exist_ok=True)
os.makedirs("Dataset/Soft", exist_ok=True)
os.makedirs("Dataset/Medium", exist_ok=True)
os.makedirs("Dataset/Hard", exist_ok=True)

os.makedirs("Figures", exist_ok=True)
os.makedirs("Figures/Baseline", exist_ok=True)
os.makedirs("Figures/Soft", exist_ok=True)
os.makedirs("Figures/Medium", exist_ok=True)
os.makedirs("Figures/Hard", exist_ok=True)

print("=" * 50)
print("Hydrogel Sensor Data Acquisition")
print("=" * 50)

# Select experiment type
print("\nSelect Experiment")
print("1. Baseline (No Phantom)")
print("2. Soft Silicone")
print("3. Medium Silicone")
print("4. Hard Silicone")

while True:
    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        phantom = "Baseline"
        break
    elif choice == "2":
        phantom = "Soft"
        break
    elif choice == "3":
        phantom = "Medium"
        break
    elif choice == "4":
        phantom = "Hard"
        break
    else:
        print("Invalid selection. Please choose 1, 2, 3, or 4.")

trial = input("Trial Number: ").strip()

notes = input("Notes (optional): ")

today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

filename = f"{phantom}_T{trial}.csv"

filepath = os.path.join("Dataset", phantom, filename)

print("\nData will be saved as:")
print(filepath)

# Connect to Arduino

PORT = "COM24"      # Change if Arduino uses another COM port
BAUDRATE = 115200

print("\nConnecting to Arduino...")

try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)

    print("✓ Arduino connected successfully!")

    # Initialize Arduino

    ser.read(19)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    time.sleep(0.5)

    print("Arduino initialized.")

   
    # Create CSV File

    outputfile = open(filepath, "w", newline="")
    writer = csv.writer(outputfile)

    writer.writerow([
        "Time (s)",
        "Voltage (V)",
        "Resistance (Ohm)"
    ])

    print("CSV file created.")

    # Initialize Data Acquisition

    dataADC = [0.0, 0.0]

    startTime = time.time()
    printTime = time.time()

    print("\nStarting data acquisition...")
    print("Press Ctrl + C to stop.\n")

    invalid_samples = 0
    
    
    # Data Acquisition Loop

    while True:

        try:

            line = ser.readline().decode("utf-8").strip()

            if not line:
             continue

            dataADC_ = line.split(",")

            if (
                len(dataADC_) == 2
                and is_float(dataADC_[0])
                and is_float(dataADC_[1])
            ):

                voltage = float(dataADC_[0])
                resistance = float(dataADC_[1])

                # Ignore invalid (negative) resistance values
                if resistance < 0:
                    invalid_samples += 1
                    continue

                elapsed_time = time.time() - startTime

                writer.writerow([
                    elapsed_time,
                    voltage,
                    resistance
                ])

                outputfile.flush()
                
                dataADC[0] = voltage
                dataADC[1] = resistance

            if (time.time() - printTime) >= 1 and any(dataADC):

                print(
                    f"Time: {time.time()-startTime:6.2f} s | "
                    f"Voltage: {dataADC[0]:6.3f} V | "
                    f"Resistance: {dataADC[1]:8.2f} Ω"
                )

                printTime = time.time()

        except UnicodeDecodeError:
            continue

except KeyboardInterrupt:

    print("\nStopping acquisition...")

    ser.close()
    outputfile.close()

    print("Arduino disconnected.")
    print("CSV file saved.")
    print(f"Invalid resistance samples removed: {invalid_samples}")

   
    # Load Recorded Data

    rawData = np.genfromtxt(
        filepath,
        delimiter=",",
        skip_header=1
    )

    if rawData.size == 0:
        print("No data was recorded.")
        raise SystemExit

    if rawData.ndim == 1:
        rawData = rawData.reshape(1, -1)

  
    # Create Figure

    figure_path = os.path.join(
        "Figures",
        phantom,
        f"{phantom}_T{trial}.png"
    )

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(10, 8),
        sharex=True
    )

    # Voltage

    ax1.plot(
        rawData[:,0],
        rawData[:,1],
        linewidth=1.5
    )

    ax1.set_title(f"{phantom} Trial {trial}")
    ax1.set_ylabel("Voltage (V)")
    ax1.set_ylim([-0.2, 5.2])
    ax1.grid(True)

    # Resistance

    ymin = np.min(rawData[:,2]) - 250
    ymax = np.max(rawData[:,2]) + 250

    ax2.plot(
        rawData[:,0],
        rawData[:,2],
        linewidth=1.5
    )

    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Resistance (Ω)")
    ax2.set_ylim([ymin, ymax])
    ax2.grid(True)

    plt.tight_layout()

    plt.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    # Experiment Summary
    
    duration = rawData[-1,0]
    samples = len(rawData)

    sampling_rate = samples / duration if duration > 0 else 0

    print("\n" + "="*50)
    print("Experiment Summary")
    print("="*50)

    print(f"Experiment     : {phantom}")
    print(f"Trial          : {trial}")
    print(f"Duration       : {duration:.2f} s")
    print(f"Samples        : {samples}")
    print(f"Sampling Rate  : {sampling_rate:.2f} Hz")

    print("\nVoltage")
    print(f"  Min          : {np.min(rawData[:,1]):.3f} V")
    print(f"  Max          : {np.max(rawData[:,1]):.3f} V")
    print(f"  Mean         : {np.mean(rawData[:,1]):.3f} V")

    print("\nResistance")
    print(f"  Min          : {np.min(rawData[:,2]):.2f} Ω")
    print(f"  Max          : {np.max(rawData[:,2]):.2f} Ω")
    print(f"  Mean         : {np.mean(rawData[:,2]):.2f} Ω")

    print("\nData saved to:")
    print(filepath)

    print("\nFigure saved to:")
    print(figure_path)

    print("\nExperiment completed successfully!")

except serial.SerialException:
    print("✗ ERROR: Could not connect to Arduino.")
    raise