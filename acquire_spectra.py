import numpy as np
import pandas as pd
from acquire_spectra_utils import (
    get_datafile, 
    param_check, 
    lorentzian_profile,
    add_white_noise,
    apply_cavity_mode_response
)
import matplotlib.pyplot as plt

def acquire_spectra(params: dict, window=30, resolution=0.001, hwhm=0.007, v_res=8206.4, Q=10000, Pmax=1.0):
    """
    For each spectral line in the data file corresponding to the molecule specified in params,
    create a local frequency grid (spanning ±window around its doubled frequency) and compute its
    broadened spectrum using a Lorentzian profile. The local spectra are then interpolated onto a 
    common grid and summed to produce the final spectrum.
    """

    # verify user input is valid
    # if not param_check(params):
        # return {
           # "success": False,
           # "text": "One of the given parameters was invalid. Please change some settings and try again.",
       # }

    # Retrieve the molecule parameter from params.
    molecule = params.get("molecule")
    
    # Use the helper function to obtain the correct data file path.
    datafile = get_datafile(molecule)
    
    # Optionally get crop_min and crop_max from params.
    crop_min = params.get("crop_min", None)
    crop_max = params.get("crop_max", None)
    
    # Read the data file.
    df = pd.read_csv(datafile, sep=r"\s+", header=None, names=["Frequency", "Intensity"])
    df["Frequency"] = pd.to_numeric(df["Frequency"], errors='coerce')
    df["Intensity"] = pd.to_numeric(df["Intensity"], errors='coerce')
    line_freq = df["Frequency"].values
    line_intensity = df["Intensity"].values

    # Constants
    c_SI = 299792458.0    # Speed of light in m/s
    vrms = 1760.0         # Helium velocity in m/s

    # Double the frequencies.
    doubled_line_freq = line_freq * 2

    # If cropping is specified, filter out spectral lines that do not contribute.
    if crop_min is not None and crop_max is not None:
        mask_lines = (doubled_line_freq + window >= crop_min) & (doubled_line_freq - window <= crop_max)
        line_freq = line_freq[mask_lines]
        line_intensity = line_intensity[mask_lines]
        doubled_line_freq = doubled_line_freq[mask_lines]

    # Collect individual spectra (local grid and corresponding spectrum).
    individual_spectra = []
    for f, I in zip(doubled_line_freq, line_intensity):
        local_grid = np.arange(f - window, f + window, resolution)
        split_val = 2 * (f / c_SI) * vrms
        split = f + split_val

        profile_main = I * lorentzian_profile(local_grid, f, hwhm)
        profile_split = I * lorentzian_profile(local_grid, split, hwhm)
        local_spectrum = profile_main + profile_split

        individual_spectra.append((local_grid, local_spectrum))
    
    # Define the overall frequency grid.
    if crop_min is not None and crop_max is not None:
        final_grid = np.arange(crop_min, crop_max, resolution)
    else:
        overall_min = min(local_grid[0] for local_grid, _ in individual_spectra)
        overall_max = max(local_grid[-1] for local_grid, _ in individual_spectra)
        final_grid = np.arange(overall_min, overall_max, resolution)
    
    final_spectrum = np.zeros_like(final_grid, dtype=float)
    
    # Interpolate each individual spectrum onto the overall grid and sum them.
    for local_grid, local_spec in individual_spectra:
        final_spectrum += np.interp(final_grid, local_grid, local_spec, left=0, right=0)

    # Add white noise to the final spectrum, depending on the number of cycles per step.
    cyclesPerStep = params.get("numCyclesPerStep")
    final_spectrum = add_white_noise(final_spectrum, cyclesPerStep, is_cavity_mode=False)

    # Apply cavity mode response
    final_spectrum = apply_cavity_mode_response(params, final_grid, final_spectrum, v_res*2, Q, Pmax)

    plt.plot(final_grid, final_spectrum)
    plt.show()

    return {
        "success": True,
        "x": final_grid.tolist(),
        "y": final_spectrum.tolist(),
    }

def main():
    params = {
        "molecule": "C7H5N",
        "crop_min": 8204 * 2,
        "crop_max": 8209 * 2,
        "numCyclesPerStep": 1
    }
    acquire_spectra(params)

if __name__ == '__main__':
    main()
