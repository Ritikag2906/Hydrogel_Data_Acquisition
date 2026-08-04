# Hydrogel-Tactile-Data-Acquisition

> Data acquisition framework for conductive hydrogel tactile sensors.

**Author:** Ritika Gupta

**Master's Thesis**

**Max Planck Institute for Intelligent Systems (MPI-IS), Stuttgart**

**University of Freiburg**

---

## Overview

This repository contains the data acquisition software developed as part of my Master's thesis, *Smart Soft Sensor Architectures for Multimodal Perception*, conducted at the Max Planck Institute for Intelligent Systems (MPI-IS) in collaboration with the University of Freiburg.

The framework acquires resistance measurements from conductive hydrogel tactile sensors through an Arduino-based acquisition system. The recorded signals are automatically saved, organized, and prepared for subsequent signal processing and self-supervised learning.

---

## Project Workflow

```text
Conductive Hydrogel Sensor
            │
            ▼
Voltage Divider Circuit
            │
            ▼
ADS1115 ADC
            │
            ▼
Arduino
            │
            ▼
Python Serial Communication
            │
            ▼
Automatic CSV Recording
            │
            ▼
Dataset Organization
            │
            ▼
Signal Processing & Machine Learning
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
│   ├── Baseline/
│   ├── Soft/
│   ├── Medium/
│   └── Hard/
│
├── Figures/
│   ├── Baseline/
│   ├── Soft/
│   ├── Medium/
│   └── Hard/
│
├── src/
│   └── hydrogel_data_acquisition.py
│
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## Features

- Arduino-based serial communication
- Automatic resistance data acquisition
- CSV data logging
- Organized dataset generation
- Automatic trial management
- Metadata recording
- Signal visualization
- Publication-quality figure generation

---

## Hardware

The acquisition system consists of:

- Conductive hydrogel tactile sensor
- Arduino Uno
- ADS1115 16-bit Analog-to-Digital Converter
- Voltage divider circuit
- USB serial communication

---

## Dataset

The dataset is organized into four experimental categories:

- Baseline
- Soft
- Medium
- Hard

Each recording is automatically stored in the appropriate folder together with its associated trial information.

---

## Technologies

- Python
- NumPy
- Pandas
- Matplotlib
- PySerial
- Arduino IDE

---

## Related Project

The recorded tactile signals are processed and used for self-supervised representation learning in the companion repository:

**Hydrogel-SSL-Tactile-Sensing**

---

## License

This repository is released under the MIT License.

---

## Contact

**Ritika Gupta**

M.Sc. Computer Science

University of Freiburg

Max Planck Institute for Intelligent Systems