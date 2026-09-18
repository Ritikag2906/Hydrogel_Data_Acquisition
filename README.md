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

The measurements are organized according to substrate hardness and surface condition. The data are processed separately for electrical and mechanical characterization and are then synchronized to enable multimodal analysis.

The current multimodal analysis investigates the relationship between the electrical response of the hydrogel sensor and mechanical loading using:

- Change in resistance (`ΔR`)
- Force
- Displacement
- Signal-to-noise ratio (SNR)
- Substrate hardness
- Surface condition / roughness condition

The processed data provide the basis for the subsequent machine-learning stage of the thesis.

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
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
        Data Storage               Instron Testing
                                          │
                                          ▼
                              Mechanical Measurements
                           (Force / Displacement /
                            Strain / Stress)
                                          │
                                          ▼
                                  Data Preprocessing
                                          │
                         ┌────────────────┴────────────────┐
                         │                                 │
                         ▼                                 ▼
                Electrical Analysis              Mechanical Analysis
                         │                                 │
                         └────────────────┬────────────────┘
                                          │
                                          ▼
                                   Synchronization
                                          │
                                          ▼
                                Multimodal Analysis
                                          │
                                          ▼
                                ML Dataset Preparation
                                          │
                                          ▼
                              Machine-Learning Analysis
```

---

## Repository Structure

```text
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
│   │   │
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
│   │
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
```

---

## Data Acquisition

The electrical acquisition system records the response of the conductive hydrogel tactile sensor during mechanical loading.

### Electrical Measurements

The Arduino-based system records:

- Time
- Voltage
- Resistance

The measurements are transferred through serial communication to Python and saved as CSV files.

The acquisition system supports repeated trials and organized storage according to the experimental condition.

### Mechanical Measurements

Mechanical measurements are collected using an Instron testing machine.

The recorded mechanical parameters include:

- Time
- Displacement
- Force
- Compressive strain
- Compressive stress

The electrical and mechanical measurements are later synchronized to enable multimodal analysis.

---

## Experimental Dataset

The main experimental dataset investigates hydrogel samples with different nominal hardness values and surface conditions.

### Smooth Surfaces

The smooth-surface experiments include four nominal hardness levels:

| Hardness |
|----------|
| H10 |
| H20 |
| H30 |
| H50 |

Two Arduino trials were recorded for the smooth-surface conditions.

The first trial is currently used as the main trial for the balanced analysis, while the additional trial is retained for repeatability analysis.

### Rough Surfaces

The rough-surface experiments combine the four hardness levels with two surface conditions:

- R30
- R40

The main rough-surface conditions are:

```text
H10_R30
H10_R40

H20_R30
H20_R40

H30_R30
H30_R40

H50_R30
H50_R40
```

Together with the four smooth-surface conditions, this results in:

**12 main experimental conditions**

Additional experiments, including `Gel` and `No_Testbed`, are retained as reference and control data.

---

## Electrical Data Analysis

Electrical data analysis is performed using:

```text
Analysis/Arduino_Analysis.py
```

The analysis extracts representative features from the resistance and voltage signals.

### Resistance Features

- Recording duration
- Number of samples
- Sampling rate
- Initial recorded resistance
- Final resistance
- Change in resistance
- Relative change in resistance
- Mean resistance
- Standard deviation of resistance
- Minimum resistance
- Maximum resistance
- Resistance range

### Voltage Features

- Initial voltage
- Final voltage
- Relative change in voltage
- Mean voltage
- Standard deviation of voltage
- Minimum voltage
- Maximum voltage
- Voltage range

The extracted electrical features are saved in:

```text
Analysis/Arduino_Results/
```

Figures generated during the electrical analysis are stored in:

```text
Figures/Arduino/
```

---

## Mechanical Data Analysis

Mechanical measurements are obtained from Instron compression tests.

The current mechanical analysis is performed using:

```text
Analysis/Instron_Smooth_vs_Rough_Analysis.py
```

The analysis extracts representative mechanical features including:

- Maximum force
- Maximum displacement
- Maximum strain
- Maximum stress
- Effective loading stiffness
- Mechanical work

Force-displacement curves and feature-level comparisons are generated for the different hardness and surface conditions.

The extracted mechanical features are saved in:

```text
Analysis/Mechanical_Results/
```

The corresponding figures are stored in:

```text
Figures/Mechanical_Smooth_vs_Rough/
```

---

## Electrical and Mechanical Synchronization

The electrical measurements from the Arduino and the mechanical measurements from the Instron are synchronized before performing the multimodal analysis.

The synchronized dataset combines:

```text
Time
Resistance
Voltage
Displacement
Force
Strain
Stress
```

The synchronization aligns the electrical and mechanical measurements using the timing of the compression experiment.

The Instron mechanical loading onset is used as the reference for aligning the two time axes.

The synchronized measurements are saved in:

```text
Analysis/Synchronized_Data/
```

The synchronization procedure is validated using individual trials and visual inspection of the electrical and mechanical signals before being applied to the main dataset.

The raw Arduino and Instron measurements remain unchanged.

---

## Multimodal Feature Analysis

The multimodal analysis is performed using:

```text
Analysis/Multimodal_Feature_Analysis.py
```

The purpose of this stage is to investigate how the electrical response of the hydrogel sensor changes with mechanical deformation and different surface conditions.

### Change in Resistance

The electrical response is represented by:

```text
ΔR = R - R0
```

where `R0` is calculated as the median resistance of the first 5% of the recorded signal.

The sign of `ΔR` is retained:

- Positive `ΔR` indicates an increase in resistance relative to `R0`.
- Negative `ΔR` indicates a decrease in resistance relative to `R0`.

### ΔR vs Force

For each hardness level, the electrical response is plotted against the applied force.

The surface conditions are compared as:

- Smooth
- R30
- R40

The analysis is performed for:

- H10
- H20
- H30
- H50

Both loading and unloading are retained so that the complete compression cycle can be observed.

The resulting figures are stored in:

```text
Figures/Multimodal/
```

### ΔR vs Displacement

The electrical response is also plotted against displacement to examine how the resistance changes with mechanical deformation.

The same four hardness levels and three surface conditions are compared.

Both loading and unloading are retained in the response curves.

The displacement plots are stored in:

```text
Figures/Multimodal/
```

### Signal-to-Noise Ratio

The signal-to-noise ratio (SNR) is calculated to evaluate the electrical response relative to the noise level of the recorded signal.

The current calculation uses the initial recorded region as the noise reference and the maximum absolute resistance change as the signal response.

The SNR is expressed in decibels:

```text
SNR (dB) = 20 log10(signal / noise)
```

The numerical SNR features are saved in:

```text
Analysis/Multimodal_Results/SNR_Features.csv
```

The SNR comparison figure is stored in:

```text
Figures/Multimodal/SNR/
```

---

## Electrical Artifacts

Some measurements contain electrical transients or artifacts that can affect the extracted features.

The H20-R30 measurement currently contains a large electrical artifact. Affected values are excluded from the relevant feature calculations where necessary.

The original synchronized CSV files are **not modified**.

Any additional measurements that are retaken will be evaluated using the same analysis procedure and compared with the existing measurements.

---

## Current Multimodal Analysis Workflow

```text
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
        └────────────────────┐
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
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
             ΔR vs        ΔR vs         SNR
              Force     Displacement
                │            │            │
                └────────────┴────────────┘
                             │
                             ▼
                      ML Dataset
                             │
                             ▼
                 Machine-Learning Analysis
```

---

## Machine-Learning Preparation

The multimodal analysis provides the basis for the machine-learning stage of the thesis.

The planned ML task is a binary classification problem:

```text
0 = No tumor-like inclusion
1 = Tumor-like inclusion present
```

The final ML dataset is intended to combine information from multiple sensing modalities, including:

- Electrical response
- Mechanical response
- Temperature
- Hardness
- Roughness

The current hardness and surface-condition experiments are primarily used for sensor characterization and preparation of the multimodal dataset.

They do not by themselves constitute the final tumor/no-tumor classification dataset.

The ML methodology will be developed after the multimodal feature analysis and dataset preparation are completed.

---

## Features

- Arduino-based electrical data acquisition
- ADS1115-based voltage measurement
- Automatic resistance calculation
- Python serial communication
- Automatic CSV data logging
- Organized experimental trial management
- Instron mechanical data processing
- Electrical feature extraction
- Mechanical feature extraction
- Electrical-mechanical synchronization
- Multimodal feature analysis
- ΔR vs Force analysis
- ΔR vs Displacement analysis
- Signal-to-noise ratio analysis
- Automated figure generation
- Preparation of multimodal datasets for machine learning

---

## Hardware

The electrical acquisition system consists of:

- Conductive hydrogel tactile sensor
- Arduino Uno
- ADS1115 16-bit Analog-to-Digital Converter
- Voltage divider circuit
- USB serial connection

Mechanical measurements are obtained using an Instron mechanical testing system.

---

## Software and Technologies

The project uses:

- Python
- NumPy
- Pandas
- Matplotlib
- PySerial
- Arduino IDE
- Arduino C/C++

Python dependencies are listed in:

```text
requirements.txt
```

---

## Reproducibility

The repository separates raw experimental data, analysis scripts, numerical results, and generated figures.

The general analysis workflow is:

```text
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
```

Raw experimental data should be treated as source data and should not be modified by the analysis scripts.

Derived data, numerical features, and figures are stored separately from the raw measurements.

---

## License

This repository is released under the MIT License.

---

## Contact

**Ritika Gupta**  
M.Sc. Computer Science  
University of Freiburg  
Max Planck Institute for Intelligent Systems[text](Dataset/Rough_H20_R30)