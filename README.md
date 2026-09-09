# Hydrogel-Tactile-Data-Acquisition

> Data acquisition and analysis framework for conductive hydrogel tactile sensors.

**Author:** Ritika Gupta

**Master's Thesis**

**Max Planck Institute for Intelligent Systems (MPI-IS), Stuttgart**

**University of Freiburg**

---

## Overview

This repository contains the data acquisition and analysis framework developed as part of my Master's thesis, *Smart Soft Sensor Architectures for Multimodal Perception*, conducted at the Max Planck Institute for Intelligent Systems (MPI-IS) in collaboration with the University of Freiburg.

The project focuses on conductive hydrogel-based tactile sensors and the acquisition of multimodal sensor data. Electrical measurements are acquired using an Arduino-based system, while mechanical measurements are obtained using an Instron testing machine.

The recorded data is organized according to the experimental conditions and processed to extract electrical and mechanical features. These features provide the basis for subsequent multimodal analysis.

---

## Project Workflow

```text
             Conductive Hydrogel Sensor
                       │
                       ▼
              Voltage Divider Circuit
                       │
                       ▼
                    ADS1115
                       │
                       ▼
                    Arduino
                       │
                       ▼
             Python Serial Acquisition
                       │
                       ▼
                 Electrical Data
             (Voltage / Resistance)
                       │
                       │
                       ├──────────────────┐
                       │                  │
                       ▼                  ▼
                Instron Testing      Data Storage
                       │
                       ▼
          Mechanical Measurements
       (Force / Displacement / Strain /
                Stress)
                       │
                       ▼
              Data Preprocessing
                       │
                       ▼
             Feature Extraction
                       │
                       ▼
          Multimodal Data Analysis

Repository Structure
Hydrogel_Data_Acquisition/

│
├── Arduino/
│   └── ADCV1.ino
│
├── Dataset/
│   ├── Arduino_Instron_Data/
│   │   ├── Gel/
│   │   ├── No_Testbed/
│   │   ├── SmoothSurface/
│   │   │   ├── Hardness_10/
│   │   │   ├── Hardness_20/
│   │   │   ├── Hardness_30/
│   │   │   └── Hardness_50/
│   │   └── RoughSurface/
│   │       ├── Rough_H10_R30/
│   │       ├── Rough_H10_R40/
│   │       ├── Rough_H20_R30/
│   │       ├── Rough_H20_R40/
│   │       ├── Rough_H30_R30/
│   │       ├── Rough_H30_R40/
│   │       ├── Rough_H50_R30/
│   │       └── Rough_H50_R40/
│   │
│   └── Instron_Data/
│       ├── SmoothSurface/
│       ├── RoughSurface/
│       └── ...
│
├── Analysis/
│   ├── Arduino_Analysis.py
│   ├── Instron_Smooth_vs_Rough_Analysis.py
│   ├── Arduino_Results/
│   └── Mechanical_Results/
│
├── Figures/
│   ├── Arduino/
│   ├── Mechanical_Smooth_vs_Rough/
│   └── Combined/
│
├── src/
│
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
Data Acquisition

The electrical acquisition system records the response of conductive hydrogel tactile sensors during mechanical loading.

The Arduino-based system records:

Time
Voltage
Resistance

The measurements are transferred through serial communication to Python, where they are automatically recorded as CSV files.

The acquisition system supports repeated trials and organized storage according to the experimental condition.

Experimental Dataset

The main experimental dataset investigates hydrogel samples with different nominal hardness values and surface conditions.

Smooth Surfaces

The smooth-surface experiments include four nominal hardness levels:

H10
H20
H30
H50

Two Arduino trials were recorded for the smooth-surface conditions. The first trial is currently used as the main trial for the balanced analysis, while additional trials are retained for repeatability analysis.

Rough Surfaces

The rough-surface experiments combine the four hardness levels with two surface conditions:

R30
R40

The main rough-surface conditions are:

H10_R30
H10_R40
H20_R30
H20_R40
H30_R30
H30_R40
H50_R30
H50_R40

Together with the four smooth-surface conditions, this gives a total of 12 main experimental conditions.

Additional experiments, including Gel and No_Testbed measurements, are retained as reference and control data.

Electrical Data Analysis

Electrical data analysis is performed using:

Analysis/Arduino_Analysis.py

The analysis extracts features from the recorded resistance and voltage signals, including:

Recording duration
Number of samples
Sampling rate
Initial recorded resistance
Final resistance
Change in resistance
Relative change in resistance
Mean resistance
Standard deviation of resistance
Minimum and maximum resistance
Resistance range
Initial voltage
Final voltage
Relative change in voltage
Voltage statistics

The extracted electrical features are saved in:

Analysis/Arduino_Results/

Figures generated during the electrical analysis are stored in:

Figures/Arduino/
Mechanical Data Analysis

Mechanical measurements are obtained from Instron compression tests.

The current mechanical analysis is performed using:

Analysis/Instron_Smooth_vs_Rough_Analysis.py

The analysis extracts representative mechanical features including:

Maximum force
Maximum displacement
Maximum strain
Maximum stress
Effective loading stiffness
Mechanical work

Force-displacement curves and feature-level comparisons are generated for the different hardness and surface conditions.

The extracted mechanical features are saved in:

Analysis/Mechanical_Results/

The corresponding figures are stored in:

Figures/Mechanical_Smooth_vs_Rough/
Electrical and Mechanical Synchronization

A further stage of the analysis is to synchronize the electrical measurements from the Arduino with the mechanical measurements from the Instron.

The planned synchronized dataset will combine:

Time
Resistance
Voltage
Displacement
Force
Strain
Stress

The synchronization will align the electrical and mechanical measurements based on the timing of the compression experiment.

This stage is being developed and validated using individual pilot trials before being applied to the complete dataset.

Features
Arduino-based electrical data acquisition
ADS1115-based voltage measurement
Automatic resistance calculation
Python serial communication
Automatic CSV data logging
Organized experimental trial management
Instron mechanical data processing
Electrical feature extraction
Mechanical feature extraction
Electrical-mechanical data synchronization
Automated figure generation
Preparation of multimodal datasets for further analysis
Hardware

The electrical acquisition system consists of:

Conductive hydrogel tactile sensor
Arduino Uno
ADS1115 16-bit Analog-to-Digital Converter
Voltage divider circuit
USB serial connection

Mechanical measurements are obtained using an Instron mechanical testing system.

Software and Technologies

The project uses:

Python
NumPy
Pandas
Matplotlib
PySerial
Arduino IDE
Arduino C/C++

Python dependencies are listed in:

requirements.txt
Reproducibility

The repository separates raw experimental data, analysis scripts, numerical results, and generated figures.

The general analysis workflow is:

Raw Experimental Data
          │
          ▼
    Analysis Scripts
          │
          ├── Electrical Analysis
          │
          ├── Mechanical Analysis
          │
          └── Synchronization
                    │
                    ▼
            Multimodal Dataset
                    │
                    ▼
             Further Analysis

Raw experimental data should be treated as source data and should not be modified by the analysis scripts.

License

This repository is released under the MIT License.

Contact

Ritika Gupta

M.Sc. Computer Science

University of Freiburg

Max Planck Institute for Intelligent Systems