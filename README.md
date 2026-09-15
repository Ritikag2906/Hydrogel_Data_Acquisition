Hydrogel-Tactile-Data-Acquisition

Data acquisition and analysis framework for conductive hydrogel tactile sensors.

Author: Ritika Gupta
Master's Thesis
Max Planck Institute for Intelligent Systems (MPI-IS), Stuttgart
University of Freiburg

Overview

This repository contains the data acquisition and analysis framework developed as part of my Master's thesis, Smart Soft Sensor Architectures for Multimodal Perception, conducted at the Max Planck Institute for Intelligent Systems (MPI-IS) in collaboration with the University of Freiburg.

The project focuses on conductive hydrogel-based tactile sensors and the acquisition of multimodal sensor data. Electrical measurements are acquired using an Arduino-based system, while mechanical measurements are obtained using an Instron testing machine.

The measurements are organized according to substrate hardness and surface condition. The data are processed individually for electrical and mechanical characterization and are then synchronized to enable multimodal analysis.

The current multimodal analysis focuses on the relationship between the electrical response of the hydrogel sensor and mechanical loading, including:

Change in resistance (ΔR)

Force

Displacement

Signal-to-noise ratio (SNR)

Hardness

Surface condition / roughness condition

The processed dataset will provide the basis for the subsequent machine-learning stage of the thesis.

Project Workflow

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
                            ├─────────────────────┐
                            │                     │
                            ▼                     ▼
                    Data Storage          Instron Testing
                                                  │
                                                  ▼
                                      Mechanical Measurements
                               (Force / Displacement / Strain /
                                        Stress)
                                                  │
                                                  ▼
                                         Data Preprocessing
                                                  │
                         ┌────────────────────────┴────────────────────┐
                         │                                             │
                         ▼                                             ▼
                Electrical Analysis                         Mechanical Analysis
                         │                                             │
                         └────────────────────────┬────────────────────┘
                                                  │
                                                  ▼
                                           Synchronization
                                                  │
                                                  ▼
                                       Multimodal Data Analysis
                                                  │
                                                  ▼
                                       ML Dataset Preparation
                                                  │
                                                  ▼
                                      Machine-Learning Analysis

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
│   ├── Arduino_Instron_Synchronization.py
│   ├── Multimodal_Feature_Analysis.py
│   ├── Arduino_Results/
│   ├── Mechanical_Results/
│   ├── Synchronized_Data/
│   └── Multimodal_Results/
│
├── Figures/
│   ├── Arduino/
│   ├── Mechanical_Smooth_vs_Rough/
│   ├── Synchronization/
│   └── Multimodal/
│
├── src/
│
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore

Data Acquisition

The electrical acquisition system records the response of the conductive hydrogel tactile sensor during mechanical loading.

The Arduino-based system records:

Time

Voltage

Resistance

The measurements are transferred through serial communication to Python and saved as CSV files.

The acquisition setup supports repeated trials and organized storage according to the experimental condition.

Mechanical measurements are collected separately using an Instron testing machine. These measurements include:

Time

Displacement

Force

Compressive strain

Compressive stress

The electrical and mechanical measurements are later synchronized for multimodal analysis.

Experimental Dataset

The main experimental dataset investigates hydrogel samples with different nominal hardness values and surface conditions.

Smooth Surfaces

The smooth-surface experiments include four nominal hardness levels:

H10

H20

H30

H50

Two Arduino trials were recorded for the smooth-surface conditions. The first trial is currently used as the main trial for the balanced analysis, while the additional trial is retained for repeatability analysis.

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

Additional experiments, including Gel and No_Testbed, are retained as reference and control data.

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

The electrical measurements from the Arduino and the mechanical measurements from the Instron are synchronized before multimodal analysis.

The synchronized dataset combines:

Time
Resistance
Voltage
Displacement
Force
Strain
Stress

The synchronization aligns the electrical and mechanical measurements using the timing of the compression experiment. The Instron mechanical loading onset is used as the reference for aligning the two time axes.

The synchronized data are saved in:

Analysis/Synchronized_Data/

The synchronization process is validated using individual trials and visual checks of the electrical and mechanical signals before applying the same procedure to the main dataset.

The raw Arduino and Instron measurements remain unchanged.

Multimodal Feature Analysis

The multimodal analysis is performed using:

Analysis/Multimodal_Feature_Analysis.py

The purpose of this stage is to investigate how the electrical response of the hydrogel sensor changes with mechanical deformation and different surface conditions.

Change in Resistance

The electrical response is represented by:

ΔR = R - R0

where R0 is calculated as the median resistance of the first 5% of the recorded resistance signal.

The sign of ΔR is retained:

Positive ΔR indicates an increase in resistance relative to R0.

Negative ΔR indicates a decrease in resistance relative to R0.

For response plots, the complete compression cycle is retained, including both loading and unloading.

ΔR vs Force

For each hardness level, the script generates a plot comparing:

Smooth

R30

R40

The four hardness levels are:

H10

H20

H30

H50

The resulting figures show the relationship between the electrical response and the applied mechanical force.

The figures are saved in:

Figures/Multimodal/

ΔR vs Displacement

The same approach is used to examine the relationship between resistance change and displacement.

The complete compression cycle is retained so that differences between loading and unloading can be observed.

The displacement plots are generated for:

H10

H20

H30

H50

and compare:

Smooth

R30

R40

Signal-to-Noise Ratio

The multimodal analysis also calculates an SNR estimate for each experimental condition.

The current SNR calculation uses the initial recorded resistance region as the noise reference and the maximum absolute resistance change as the signal response.

The SNR is expressed in decibels:

SNR (dB) = 20 log10(signal / noise)

The SNR comparison is presented as a grouped bar chart showing the different surface conditions for each hardness level.

The numerical SNR results are saved in:

Analysis/Multimodal_Results/SNR_Features.csv

The corresponding figure is stored in:

Figures/Multimodal/SNR/

Electrical Artifacts

Some measurements contain electrical transients or artifacts. These are treated separately from the physical sensor response.

In particular, the H20-R30 measurement contains a large electrical artifact. Where necessary, affected values are excluded from feature calculations or flagged during analysis.

The raw synchronized CSV files are not modified.

Current Multimodal Analysis Workflow

The current analysis follows:

Raw Arduino Data
        │
        ▼
Electrical Analysis
        │
        │
Raw Instron Data
        │
        ▼
Mechanical Analysis
        │
        └───────────────┐
                        │
                        ▼
                  Synchronization
                        │
                        ▼
             Synchronized Dataset
                        │
                        ▼
            Multimodal Feature Analysis
                        │
             ┌──────────┼───────────┐
             │          │           │
             ▼          ▼           ▼
          ΔR vs       ΔR vs       SNR
           Force    Displacement
             │          │           │
             └──────────┴───────────┘
                        │
                        ▼
                 ML Dataset
                        │
                        ▼
              Machine-Learning Stage

Machine-Learning Preparation

The multimodal analysis provides the foundation for the machine-learning stage of the thesis.

The planned ML task is a binary classification problem:

0 = No tumor-like inclusion
1 = Tumor-like inclusion present

The final ML dataset is intended to combine information from multiple modalities, including:

Electrical response

Mechanical response

Temperature

Hardness

Roughness

The current hardness and surface-condition experiments are primarily used for sensor characterization and preparation of the multimodal dataset. They do not by themselves constitute the final tumor/no-tumor classification dataset.

The ML methodology will be developed after the multimodal feature analysis and dataset preparation are completed.

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

Electrical-mechanical synchronization

Multimodal feature analysis

ΔR vs Force analysis

ΔR vs Displacement analysis

Signal-to-noise ratio analysis

Automated figure generation

Preparation of multimodal datasets for machine learning

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
           Synchronized Dataset
                    │
                    ▼
        Multimodal Feature Analysis
                    │
                    ▼
             ML Dataset
                    │
                    ▼
        Machine-Learning Analysis

Raw experimental data should be treated as source data and should not be modified by the analysis scripts.

Derived data, numerical features, and figures are stored separately from the raw measurements.

License

This repository is released under the MIT License.

Contact

Ritika Gupta
M.Sc. Computer Science
University of Freiburg
Max Planck Institute for Intelligent Systems