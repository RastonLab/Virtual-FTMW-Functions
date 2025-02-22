import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def gaussian_broadening(datafile="HCCCN_2.lin"):
    """
    Reads spectral line data from a file and applies standard Gaussian broadening
    (using a fixed FWHM of 300 MHz) across a frequency grid from 2 to 40 GHz.
    Saves a full-range plot (broadened_spectrum.png) and CSV data (spectrum.csv).
    """
    # ---------------------------
    # Step 1: Read the Data File
    # ---------------------------
    df = pd.read_csv(datafile, sep="\t", header=None, names=["Frequency", "Intensity"])
    line_freq = df["Frequency"].values  # in MHz
    line_intensity = df["Intensity"].values

    # -------------------------------------------------------
    # Step 2: Create a Fine Frequency Grid (2–40 GHz Range)
    # -------------------------------------------------------
    freq_grid = np.arange(2000, 40000, 1)  # in MHz

    # -----------------------------------------------
    # Step 3: Apply Gaussian Broadening to Each Line
    # -----------------------------------------------
    FWHM = 300.0  # MHz
    # Convert FWHM to Gaussian standard deviation
    sd = FWHM / (2 * np.sqrt(2 * np.log(2)))  # ≈ 127.3 MHz

    spectrum = np.zeros_like(freq_grid, dtype=float)
    for f, I in zip(line_freq, line_intensity):
        # Gaussian parametric function: I * exp[-0.5*((freq - f)/sd)**2]
        spectrum += I * np.exp(-0.5 * ((freq_grid - f) / sd) ** 2)

    # --------------------------------------------------
    # Step 4: Plot the Broadened Spectrum (2–40 GHz)
    # --------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(freq_grid / 1000, spectrum, lw=2, label="Standard Gaussian Broadening")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Intensity")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("broadened_spectrum.png", dpi=300)
    plt.show()

    # ------------------------------------------------------
    # Step 5: Save the Broadened Spectrum to a CSV File
    # ------------------------------------------------------
    output_df = pd.DataFrame({
        "Frequency (GHz)": freq_grid / 1000,
        "Intensity": spectrum
    })
    output_df.to_csv("spectrum.csv", index=False)

def doppler_broadening(datafile="HCCCN_2.lin"):
    """
    Reads spectral line data from a file, splits each spectral line into two components,
    and applies Doppler broadening according to:
    
      split = 2 * (f_ref / c_SI) * vrms
      FWHM  = 2 * (f / c_SI) * np.sqrt(2 * k * T * ln2 / m_molecule)
      
    (with appropriate SI units conversion).
    
    The zoomed-in spectrum is plotted around the reference line and saved as a PNG and CSV.
    """
    # Physical constants (SI units)
    c_SI = 299792458.0         # Speed of light in m/s
    vrms = 1367.31             # Root-mean-squared velocity in m/s
    T = 1.0                    # Temperature in K
    k = 1.380649 * 10e-23           # Boltzmann constant in J/K
    m_molecule = 51.0294 * 1.66054e-27  # Molecular mass in kg
    ln2 = np.log(2)

    # ---------------------------
    # Read the Data File
    # ---------------------------
    df = pd.read_csv(datafile, sep="\t", header=None, names=["Frequency", "Intensity"])
    line_freq = df["Frequency"].values  # in MHz
    line_intensity = df["Intensity"].values

    # Convert line frequencies from MHz to Hz for SI-consistency
    line_freq_Hz = line_freq * 1e6

    # For the zoomed-in plot, choose the first spectral line as a reference.
    f_ref = line_freq_Hz[0]  # reference frequency in Hz

    # Compute the splitting for the reference line:
    split_ref = 2 * (f_ref / c_SI) * vrms  # in Hz

    # Define a zoom window around the reference line.
    margin = 2 * split_ref
    f_min_zoom = f_ref - margin
    f_max_zoom = f_ref + margin
    freq_grid_zoom = np.linspace(f_min_zoom, f_max_zoom, 1000)

    # Initialize the zoomed spectrum array
    spectrum = np.zeros_like(freq_grid_zoom, dtype=float)

    # Loop over each spectral line, split it into two components, and add the corresponding Gaussians.
    for f, I in zip(line_freq_Hz, line_intensity):
        # Compute splitting for this line:
        split_val = 2 * (f / c_SI) * vrms  # in Hz
        print(split_val/1e9)
        
        # Compute Doppler FWHM for this line:
        FWHM = 2 * (f / c_SI) * np.sqrt(2 * k * T * ln2 / m_molecule)  # in Hz
        sd = FWHM / (2 * np.sqrt(2 * ln2))
        
        # Add two Gaussian profiles: one at (f - split) and one at (f + split)
        spectrum += I * np.exp(-0.5 * ((freq_grid_zoom - (f - split_val)) / sd) ** 2)
        spectrum += I * np.exp(-0.5 * ((freq_grid_zoom - (f + split_val)) / sd) ** 2)

    # Plot the zoomed-in, split and Doppler broadened spectrum.
    plt.figure(figsize=(10, 6))
    # Dividing by 1e9 converts Hz to GHz for display.
    plt.plot(freq_grid_zoom / 1e9, spectrum, lw=2, label="Doppler Broadened")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Intensity")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("zoomed_split_broadened_spectrum.png", dpi=300)
    plt.show()

    # Save the zoomed-in spectrum to a CSV file.
    output_zoom_df = pd.DataFrame({
        "Frequency (Ghz)": freq_grid_zoom / 1e9,
        "Intensity": spectrum
    })
    output_zoom_df.to_csv("zoomed_split_broadened_spectrum.csv", index=False)

def main():
    # Specify the data file name
    datafile = "HCCCN_2.lin"
    
    # Call the original broadening function
    gaussian_broadening(datafile)
    
    # Call the Doppler splitting & broadening function
    doppler_broadening(datafile)

if __name__ == '__main__':
    main()
