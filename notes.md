# processing.py Notes

## **generate_spectrum**

- **Function:**  
  *Generates a raw spectrum using Radis’s* **calc_spectrum()**.
  
- **Uses:**  
  **calc_wstep()** *from* **processing_utils.py** *to calculate the* <u>**wavenumber step size (wstep)**</u>.
  - **wstep:**  
    *Determines the spacing between points on the wavenumber grid used to calculate the spectrum.*

- **Parameters:**
  - **resolution (float):**  
    *This value determines the base step size. The function checks for several specific values (e.g.,* **1**, **0.5**, **0.25**, *etc.).*
  - **zero_fill (int):**  
    *Adjusts the resolution further. "Zero filling" is a technique in signal processing to increase the number of data points by interpolating between them. A higher* **zero_fill** *value results in a smaller step size (i.e., a finer grid).*

- **Spectrum Calculation:**  
  *The function attempts to calculate the spectrum by calling* **calc_spectrum()**.

---

## **process_spectrum**

- **Function:**  
  *Simulates how a spectrometer processes a raw spectrum by accounting for the effects of various instrument components such as the light source, beamsplitter, cell windows, and detector.*

- **Inputs:**
  - **params:**  
    *A dictionary containing user-specified parameters (e.g., type of beamsplitter, window material, detector type, scan settings, and wavelength cropping limits).*
  - **raw_spectrum:**  
    *The initial spectrum produced by* **generate_spectrum**.

- **Returns:**  
  *A processed* **Spectrum** *object that reflects the cumulative impact of the simulated spectrometer components.*

- **Key Steps in the Function:**

  - **raw_spectrum.get_wavenumber():**  
    *Retrieves the array of wavenumber values (the x-axis) from the raw spectrum. This is essential because all additional component spectra are generated to match these wavenumbers.*

  - **get_component_spectra():**  
    *Generates eight different spectra—each representing a component of an FTIR (Fourier Transform Infrared) spectrometer. These components include:*
    - *The light source (a blackbody spectrum).*
    - *Beamsplitters.*
    - *Cell windows.*
    - *Detector responses.*

  - **Component Multiplication with SerialSlabs:**
    - Uses **SerialSlabs()** to *multiply the transmittance values* of all the individual spectra (stored in the list **slabs**).
    - <u>**SerialSlabs**</u> *simulates the cumulative effect of each optical component (gas sample, light source, beamsplitter, cell windows, detector, etc.) on the overall spectrum.*
    - *The parameter* **modify_inputs="True"** *indicates that the function is allowed to modify its input data during processing.*

  - **Simulating Multiple Scans with multiscan:**
    - *The resulting spectrum from* **SerialSlabs** *is passed into* **multiscan()**.
    - **multiscan()** *simulates the effect of performing multiple scans of the spectrum, which can enhance the signal or simulate averaging. The number of scans is specified by* **params["scan"]**.

  - **Cropping the Final Spectrum:**
    - *After processing, the spectrum is cropped to a specific wavenumber range using* **spectrum.crop()**.
    - **spectrum.crop()** *takes two parameters:*
      - **params["waveMin"]:** *The lower limit of the wavenumber range.*
      - **params["waveMax"]:** *The upper limit of the wavenumber range.*
    - *This step ensures that only the relevant portion of the spectrum is returned, matching user-defined limits.*

---

## Additional Context in processing.py

- **Integration of Functions:**
  - **generate_spectrum** and **process_spectrum** work together to first create a raw spectrum and then modify it to mimic a real spectrometer.
  - **calc_wstep()** *(from processing_utils.py)* is used by **generate_spectrum** to determine the <u>**wavenumber grid spacing (wstep)**</u>, a critical parameter for accurate spectrum generation.

- **Overall Workflow:**
  1. **Step 1:**  
     **generate_spectrum** creates the initial raw spectrum using **calc_spectrum()** from the Radis library.
  2. **Step 2:**  
     **process_spectrum** refines this spectrum by:
      - Generating component-specific spectra via **get_component_spectra()**.
      - Combining these components using **SerialSlabs**, **multiscan**, and **spectrum.crop()** to simulate the full experimental setup.
  - *The final output is a* **Spectrum** *object that closely resembles what a real spectrometer would record.*
