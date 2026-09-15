import serial
import csv
import time
import os
from datetime import datetime

# --------------------------------------------------
# 1. Connect to Arduino
# --------------------------------------------------

arduino = serial.Serial('COM24', 9600, timeout=2)

# Give Arduino a moment to reset
time.sleep(2)

print("Connected to Arduino!")


# --------------------------------------------------
# 2. Data storage folder
# --------------------------------------------------

folder = r'C:\Users\rgupta\Desktop\Master thesis\Hydrogel_Data_Acquisition\Dataset'

os.makedirs(folder, exist_ok=True)


# --------------------------------------------------
# 3. Create a unique filename
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

    # CSV header
    writer.writerow([
        'Date_Time',
        'Elapsed_Time_s',
        'Temperature_C',
        'Temperature_F',
        'Humidity_percent',
        'Heat_Index_C',
        'Heat_Index_F'
    ])

    print("Recording data...")
    print("Press Ctrl+C in the console to stop.\n")

    try:

        while True:

            # Read line from Arduino
            line = arduino.readline().decode(
                'utf-8',
                errors='ignore'
            ).strip()

            if line:
                print(line)

            # Check for a valid DHT reading
            if 'Humidity:' in line and 'Temperature:' in line:

                try:

                    # ------------------------------------------
                    # Extract humidity
                    # ------------------------------------------

                    humidity = float(
                        line.split('Humidity:')[1]
                        .split('%')[0]
                        .strip()
                    )

                    # ------------------------------------------
                    # Extract Celsius temperature
                    # ------------------------------------------

                    temperature_c = float(
                        line.split('Temperature:')[1]
                        .split('°C')[0]
                        .strip()
                    )

                    # ------------------------------------------
                    # Extract Fahrenheit temperature
                    # ------------------------------------------

                    temperature_f = float(
                        line.split('°C')[1]
                        .split('°F')[0]
                        .strip()
                    )

                    # ------------------------------------------
                    # Extract heat index in Celsius
                    # ------------------------------------------

                    heat_index_c = float(
                        line.split('Heat index:')[1]
                        .split('°C')[0]
                        .strip()
                    )

                    # ------------------------------------------
                    # Extract heat index in Fahrenheit
                    # ------------------------------------------

                    heat_index_f = float(
                        line.split('°C')[3]
                        .split('°F')[0]
                        .strip()
                    )

                    # ------------------------------------------
                    # Time
                    # ------------------------------------------

                    now = datetime.now()

                    timestamp = now.strftime(
                        '%Y-%m-%d %H:%M:%S'
                    )

                    elapsed_time = (
                        now - start_time
                    ).total_seconds()

                    # ------------------------------------------
                    # Save to CSV
                    # ------------------------------------------

                    writer.writerow([
                        timestamp,
                        round(elapsed_time, 2),
                        temperature_c,
                        temperature_f,
                        humidity,
                        heat_index_c,
                        heat_index_f
                    ])

                    # Make sure data is written immediately
                    file.flush()

                    print(
                        f"Saved | "
                        f"{elapsed_time:.1f} s | "
                        f"T = {temperature_c:.2f} °C | "
                        f"H = {humidity:.2f} % | "
                        f"HI = {heat_index_c:.2f} °C"
                    )

                except (ValueError, IndexError):

                    # Ignore lines that cannot be parsed
                    pass

    except KeyboardInterrupt:

        print("\nRecording stopped.")
        print(f"Data saved to:")
        print(filename)

    finally:

        arduino.close()
        print("Arduino connection closed.")