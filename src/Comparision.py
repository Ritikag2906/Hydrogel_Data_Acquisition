import pandas as pd
import matplotlib.pyplot as plt
import glob

# ---------------------------------------------------------
# Folder containing the two hydrogel test files
# ---------------------------------------------------------

folder = r"C:\Users\rgupta\Desktop\Master thesis\Hydrogel_Data_Acquisition\Dataset\Instron_Data\comparision test"


# ---------------------------------------------------------
# Load the two files
# ---------------------------------------------------------

paam_file = glob.glob(folder + r"\PaAm_Trial_1_2.*")[0]
composite_file = glob.glob(folder + r"\Hardness_notestbed_Trial01.*")[0]

paam = pd.read_csv(paam_file)
composite = pd.read_csv(composite_file)


# ---------------------------------------------------------
# Convert stress and strain to numerical values
# ---------------------------------------------------------

paam["strain"] = pd.to_numeric(
    paam["Compressive strain (Displacement)"],
    errors="coerce"
)

paam["stress"] = pd.to_numeric(
    paam["Compressive stress"],
    errors="coerce"
)

composite["strain"] = pd.to_numeric(
    composite["Compressive strain (Displacement)"],
    errors="coerce"
)

composite["stress"] = pd.to_numeric(
    composite["Compressive stress"],
    errors="coerce"
)


# ---------------------------------------------------------
# Remove non-numerical rows
# ---------------------------------------------------------

paam = paam.dropna(subset=["strain", "stress"])
composite = composite.dropna(subset=["strain", "stress"])


# ---------------------------------------------------------
# Select the loading part of the test
# ---------------------------------------------------------

paam_loading = paam[paam["Cycle count"] == 0]
composite_loading = composite[composite["Cycle count"] == 0]


# ---------------------------------------------------------
# Convert stress from MPa to kPa
# ---------------------------------------------------------

paam_loading["stress_kPa"] = paam_loading["stress"] * 1000
composite_loading["stress_kPa"] = composite_loading["stress"] * 1000


# ---------------------------------------------------------
# Plot stress-strain curves
# ---------------------------------------------------------

plt.figure(figsize=(8, 6))

plt.plot(
    paam_loading["strain"],
    paam_loading["stress_kPa"],
    linewidth=2.5,
    label="PAAm"
)

plt.plot(
    composite_loading["strain"],
    composite_loading["stress_kPa"],
    linewidth=2.5,
    label="Engineered Hydrogel"
)


# ---------------------------------------------------------
# Format the graph
# ---------------------------------------------------------

plt.xlabel("Compressive strain (%)", fontsize=13)
plt.ylabel("Compressive stress (kPa)", fontsize=13)

plt.title(
    "Compressive Stress–Strain Comparison",
    fontsize=15
)

plt.xlim(0, 22)
plt.ylim(0, 10)

plt.grid(True, alpha=0.25)

plt.legend(
    fontsize=11,
    frameon=True
)

plt.tight_layout()

plt.show()