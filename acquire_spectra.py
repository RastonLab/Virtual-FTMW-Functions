import numpy as np
import pandas as pd
from acquire_spectra_utils import (
    get_datafile, 
    lorentzian_profile,
    add_white_noise,
    apply_cavity_mode_response,
    param_check,
)
from radis import Spectrum
from specutils.fitting import find_lines_threshold

def acquire_spectra(params: dict, window=25, resolution=0.001, fwhm=0.007, Q=10000, Pmax=1.0):
    """
    For each spectral line in the data file corresponding to the molecule specified in params,
    create a local frequency grid (spanning ±window around its doubled frequency) and compute its
    broadened spectrum using a Lorentzian profile. The local spectra are then interpolated onto a 
    common grid and summed to produce the final spectrum.
    """
    # verify user input is valid
    if not param_check(params):
        return {
            "success": False,
            "error": "One of the given parameters was invalid. Please change some settings and try again.",
        }
    
    # Retrieve the molecule parameter from params.
    molecule = params.get("molecule")

    # Retrieve vres parameter from params.
    v_res = params.get("vres")
    
    # Use the helper function to obtain the correct data file path.
    datafile = get_datafile(molecule)
    
    # Determine cropping bounds based on frequency mode.
    frequencyMode = params.get("acquisitionType", "single")
    if frequencyMode == "single":
        crop_min = v_res - window
        crop_max = v_res + window
    else:
        frequency_min = params.get("frequencyMin")
        frequency_max = params.get("frequencyMax")
        if frequency_min is None or frequency_max is None:
            raise ValueError("For frequency range mode, 'frequencyMin' and 'frequencyMax' must be provided.")
        crop_min = frequency_min - window
        crop_max = frequency_max + window
    
    # Read the data file.
    df = pd.read_csv(datafile, sep=r"\s+", header=None, names=["Frequency", "Intensity"])
    df["Frequency"] = pd.to_numeric(df["Frequency"], errors='coerce')
    df["Intensity"] = pd.to_numeric(df["Intensity"], errors='coerce')
    line_freq = df["Frequency"].values
    line_intensity = df["Intensity"].values

    # Constants
    c_SI = 299792458.0    # Speed of light in m/s
    vrms = 1760.0         # Helium velocity in m/s

    # Filter out spectral lines that are outside the cropping bounds.
    if crop_min is not None and crop_max is not None:
        mask_lines = (line_freq + window >= crop_min) & (line_freq - window <= crop_max)
        line_intensity = line_intensity[mask_lines]
        line_freq = line_freq[mask_lines]

    # Collect individual spectra (local grid and corresponding spectrum).
    individual_spectra = []
    for f, I in zip(line_freq, line_intensity):
        local_grid = np.arange(f - window, f + window, resolution)
        split_val = (f / c_SI) * vrms
        add_split = (f + split_val)
        subtract_split = (f - split_val)

        profile_main = I * lorentzian_profile(local_grid, add_split, fwhm)
        profile_split = I * lorentzian_profile(local_grid, subtract_split, fwhm)
        
        local_spectrum = profile_main + profile_split

        individual_spectra.append((local_grid, local_spectrum))
    
    # Define the overall frequency grid.
    final_grid = np.arange(crop_min, crop_max, resolution)
    final_spectrum = np.zeros_like(final_grid, dtype=float)
    
    # Interpolate each individual spectrum onto the overall grid and sum them.
    for local_grid, local_spec in individual_spectra:
        final_spectrum += np.interp(final_grid, local_grid, local_spec, left=0, right=0)

    # Add white noise to the final spectrum, depending on the number of cycles per step.
    cyclesPerStep = params.get("numCyclesPerStep")
    final_spectrum = add_white_noise(final_spectrum, cyclesPerStep, is_cavity_mode=False)

    # Apply cavity mode response
    final_spectrum = apply_cavity_mode_response(params, final_grid, final_spectrum, v_res, Q, Pmax)

    # Take absolute value of the final spectrum.
    final_spectrum = np.abs(final_spectrum)

    output_df = pd.DataFrame({
        "Frequency (MHz)": final_grid,
        "Intensity": final_spectrum
    })

    # Format the Frequency column to show 3 decimals and the Intensity column in scientific notation with 4 significant figures.
    output_df['Frequency (MHz)'] = output_df['Frequency (MHz)'].apply(lambda x: f"{x:.3f}")
    output_df['Intensity'] = output_df['Intensity'].apply(lambda x: f"{x:.3e}")

    output_df.to_csv("spectrum.csv", index=False)

    return {
        "success": True,
        "x": final_grid.tolist(),
        "y": final_spectrum.tolist(),
    }

def find_peaks(x_data: list[float], y_data: list[float], threshold: float = 0) -> dict:
    """
    Filters the provided data and returns only the x and y values 
    where the y value meets or exceeds the threshold.

    Parameters:
        x_data (list[float]): The x-values of the data.
        y_data (list[float]): The y-values of the data.
        threshold (float): The minimum y-value required to consider 
                           a point as a peak.

    Returns:
        dict: A dictionary containing:
              - "success": A boolean indicating if the operation succeeded.
              - "peaks": A dictionary mapping x-values (rounded to 4 decimals) 
                         to their y-values (rounded to 4 decimals) for the points 
                         above the threshold.
              - "error": (Optional) An error message if an exception was encountered.
    """
    try:
        peaks = {}
        # Iterate over paired x and y values
        for x, y in zip(x_data, y_data):
            # Check if the y value is above or equal to the threshold
            if y >= threshold:
                peaks[round(x, 4)] = round(y, 4)
        return {"success": True, "peaks": peaks}
    except Exception as e:
        return {"success": False, "error": f"An error occurred: {e}"}