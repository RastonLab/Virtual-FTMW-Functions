# Virtual‑FTMW‑Functions

This repository provides the Flask back‑end for the Raston Lab [Virtual FTMW Spectrometer](https://github.com/FTMW-Scientific-Simulator/Virtual-FTMW-Spectrometer).

## Flask

* app.py

  * Initializes a Flask application with CORS enabled.
  * Reads `version.txt` (if present) and exposes it via `app.config["VERSION"]`.
  * Defines three routes:

    * **GET /**
      * Returns a simple HTML title showing the API name and version.

    * **POST /acquire\_spectrum**
      * Parses incoming JSON parameters and forwards them to `acquire_spectra` in `acquire_spectra.py`.
      * Returns JSON with success status and arrays of X and Y values.

    * **POST /find\_peaks**
      * Parses incoming JSON containing `x`, `y`, and `threshold`, then calls `find_peaks` in `acquire_spectra.py`.
      * Returns JSON with success status and a mapping of peak frequencies to intensities.

  * When run as a script, listens on `0.0.0.0:5001` (debug off by default).

## Utilities

* acquire_spectra_utils.py

  * Contains helper functions shared by acquisition and peak‑finding logic:

    * `get_datafile(molecule, directory="linelists")`
      * Maps a molecule string to a local data filename and returns its full path.
      * Raises `ValueError` if no mapping exists.

    * `param_check(params)`
      * Verifies that the incoming parameter dictionary has exactly the expected keys and no null values.
      * Returns `True` if all checks pass, otherwise `False`.

    * `lorentzian_profile(grid, center, fwhm)`
      * Generates a Lorentzian line shape on `grid`, centered at `center` with given full width at half maximum.

    * `add_white_noise(spectrum, num_cycles_per_step, is_cavity_mode)`
      * Adds Gaussian noise scaled by `num_cycles_per_step`; uses different noise levels for cavity mode.

    * `apply_cavity_mode_response(params, frequency_grid, spectrum, v_res=8206.4, Q=10000, Pmax=1.0)`
      * Applies one or more cavity‑mode filter functions to `spectrum`, based on `acquisitionType`.
      * Adds white noise to the cavity response before multiplying it into the spectrum.

## Acquisition and Peak Finding

* acquire_spectra.py

  * Implements two main functions:

  ### `acquire_spectra(params, window=25, resolution=0.001, fwhm=0.007, Q=10000, Pmax=1.0)`

  1. Validates `params` with `param_check`. Returns error JSON if invalid.
  2. Extracts molecule name and resolution parameter `vres`.
  3. Loads line list data via `get_datafile`, reads into a DataFrame, and filters by frequency bounds.
  4. For each spectral line:
     * Builds a local frequency grid around the line center ± `window`.
     * Computes two Lorentzian components (Doppler‑shifted split peaks).
     * Sums them into a local spectrum.
     
  5. Defines a global frequency grid (`crop_min` to `crop_max`) and interpolates all local spectra onto it.
  6. Adds white noise and applies cavity mode response.
  7. Returns JSON:

     ```json
     {
       "success": true,
       "x": ["freq1","freq2",...],
       "y": ["int1","int2",...]
     }
     ```

  ### `find_peaks(x_data, y_data, threshold=0, min_distance=100)`
  * Converts inputs to NumPy arrays and calls SciPy’s `find_peaks`.
  * Catches exceptions and returns an error JSON if something goes wrong.
  * Builds and returns a dictionary mapping each peak frequency (to 4 decimal places) to its intensity (to 4 decimals).

## Installation

```bash
git clone https://github.com/FTMW-Scientific-Simulator/Virtual-FTMW-Spectrometer
cd Virtual-FTMW-Functions
python3 -m venv .venv
pip install -r requirements.txt
python app.py
```

## The Process - Breakdown of `app.py`

This section describes how incoming requests are handled:

* **Version handling**
  * On startup, attempts to read `version.txt`. If found, sets `app.config["VERSION"]`.
  * The root route displays this version in the HTML header.

* **Spectrum acquisition**
  * `POST /acquire_spectrum` → calls `acquire_spectra` → returns spectrum JSON.

* **Peak finding**
  * `POST /find_peaks` → calls `find_peaks` → returns peaks JSON.

## Function Details

### acquire_spectra_utils.py

#### get_datafile

Returns the path to a line list file for the requested molecule. Mappings:

```python
{
  "C6H5CN": "C6H5CN.dat",
  "HC7N":   "HC7N.dat",
  …
}
```

#### param_check

Ensures exactly 11 keys: `molecule, stepSize, frequencyMin, frequencyMax, numCyclesPerStep, microwavePulseWidth, mwBand, repetitionRate, molecularPulseWidth, acquisitionType, vres`.

#### lorentzian_profile

`(1/pi) * (hwhm / ((grid - center)**2 + hwhm**2))` where `hwhm = fwhm/2`.

#### add_white_noise

Draws from `np.random.normal(0, noise_level, spectrum.shape)` with `noise_level` scaled by `1/sqrt(num_cycles_per_step)`.

#### apply_cavity_mode_response

* **single mode**: one Lorentzian filter at `vres`.
* **range mode**: sum of Lorentzian filters spaced by `stepSize`.

### acquire_spectra.py

#### Spectrum generation

* Reads frequency/intensity pairs from the line list.
* Filters by `vres +/- window` or `[frequencyMin-window, frequencyMax+window]`.
* For each line, makes two Lorentzian peaks to simulate Doppler splitting.
* Interpolates and sums onto a global grid.
* Adds noise and cavity response, then takes absolute value.

#### Peak finding

* Uses `scipy.signal.find_peaks(y, height=threshold, distance=min_distance)`.
* Maps results to a JSON of `{ "freq": "intensity" }` entries.

