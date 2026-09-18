import serial
import csv
import time
import os
import re
from datetime import datetime

# --------------------------------------------------
# 1. Connect to Arduino
# --------------------------------------------------

arduino = serial.Serial('COM24', 9600, timeout=2)

# Give Arduino time to reset
time.sleep(2)

print("Connected to Arduino!")


# --------------------------------------------------
# 2. Data storage folder
# --------------------------------------------------

folder = r'C:\Users\rgupta\Desktop\Master thesis\Hydrogel_Data_Acquisition\Dataset\temperature'

os.makedirs(folder, exist_ok=True)


# --------------------------------------------------
# 3. Create unique filename
# --------------------------------------------------

start_time = datetime.now()

filename = os.path.join(
    folder,
    f'DHT22_{start_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
)

print(f"Saving data to:\n{filename}\n")


# --------------------------------------------------
# 4. Open CSV file
# --------------------------------------------------

with open(filename, 'w', newline='') as file:

    writer = csv.writer(file)

    writer.writerow([
        'Date_Time',
        'Elapsed_Time_s',
        'Temperature_C',
        'Temperature_F',
        'Humidity_percent',
        'Heat_Index_C',
        'Heat_Index_F'
    ])

    file.flush()

    print("Recording data...")
    print("Press Ctrl+C in the console to stop.\n")

    try:

        while True:

            # Read one line from Arduino
            line = arduino.readline().decode(
                'utf-8',
                errors='ignore'
            ).strip()

            if not line:
                continue

            print(line)

            # --------------------------------------------------
            # Extract humidity
            # --------------------------------------------------

            humidity_match = re.search(
                r'Humidity:\s*([0-9.]+)%',
                line
            )

            # --------------------------------------------------
            # Extract Celsius temperature
            # --------------------------------------------------

            temperature_c_match = re.search(
                r'Temperature:\s*([0-9.]+)',
                line
            )

            # --------------------------------------------------
            # Extract Fahrenheit temperature
            # --------------------------------------------------

            temperature_f_match = re.search(
                r'Temperature:\s*[0-9.]+°C\s*([0-9.]+)°F',
                line
            )

            # --------------------------------------------------
            # Extract heat index Celsius
            # --------------------------------------------------

            heat_index_c_match = re.search(
                r'Heat index:\s*([0-9.]+)',
                line
            )

            # --------------------------------------------------
            # Extract heat index Fahrenheit
            # --------------------------------------------------

            heat_index_f_match = re.search(
                r'Heat index:\s*[0-9.]+°C\s*([0-9.]+)°F',
                line
            )

            # --------------------------------------------------
            # Save only if all values were found
            # --------------------------------------------------

            if (
                humidity_match
                and temperature_c_match
                and temperature_f_match
                and heat_index_c_match
                and heat_index_f_match
            ):

                humidity = float(
                    humidity_match.group(1)
                )

                temperature_c = float(
                    temperature_c_match.group(1)
                )

                temperature_f = float(
                    temperature_f_match.group(1)
                )

                heat_index_c = float(
                    heat_index_c_match.group(1)
                )

                heat_index_f = float(
                    heat_index_f_match.group(1)
                )

                # --------------------------------------------------
                # Time
                # --------------------------------------------------

                now = datetime.now()

                timestamp = now.strftime(
                    '%Y-%m-%d %H:%M:%S'
                )

                elapsed_time = (
                    now - start_time
                ).total_seconds()

                # --------------------------------------------------
                # Write data
                # --------------------------------------------------

                writer.writerow([
                    timestamp,
                    round(elapsed_time, 2),
                    temperature_c,
                    temperature_f,
                    humidity,
                    heat_index_c,
                    heat_index_f
                ])

                # Save immediately
                file.flush()

                print(
                    f"✓ SAVED | "
                    f"T = {temperature_c:.2f} °C | "
                    f"H = {humidity:.2f} % | "
                    f"HI = {heat_index_c:.2f} °C"
                )

    except KeyboardInterrupt:

        print("\nRecording stopped.")

    finally:

        arduino.close()

        print("Arduino connection closed.")
        print(f"\nData saved to:\n{filename}")