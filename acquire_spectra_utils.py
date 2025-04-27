import os
import numpy as np

def get_datafile(molecule: str, directory: str = "linelists") -> str:
    """
    Return the full path to the data file corresponding to the given molecule.
    The mapping between molecule (chemical formula) and actual data file is defined
    in the dictionary below.
    """
    molecule_to_file = {
        "C6H5CN": "C6H5CN.dat",
        "HC7N": "HC7N.dat",
        "CH2CHCN": "CH2CHCN.dat",
        "CH2CHOH": "CH2CHOH.dat",
        "HOCH2CH2OH": "HOCH2CH2OH.dat",
        "NH2CONH2": "NH2CONH2.dat",
        "OC3S": "OC3S.dat",
        "OCS": "OCS.dat",
    }
    if molecule not in molecule_to_file:
        raise ValueError(f"No data file mapping found for molecule '{molecule}'.")
    filename = molecule_to_file[molecule]
    return os.path.join(directory, filename)

def param_check(params: dict[str, object]) -> bool:
    """
    Parses user provided parameters for validity.
    """

    # check if number of parameters is correct
    if len(params) != 11:
        print("incorrect amount of params. total params: %s" % (len(params)))
        return False

    # check if parameter names are correct
    valid_params = [
        "molecule",
        "stepSize",
        "frequencyMin",
        "frequencyMax",
        "numCyclesPerStep",
        "microwavePulseWidth",
        "mwBand",
        "repetitionRate",
        "molecularPulseWidth",
        "acquisitionType",
        "vres",
    ]

    for key, value in params.items():
        if (key not in valid_params) or (params[key] is None):
            print(f"  error with key: {key}. Value is: {value}")
            return False

    return True

def lorentzian_profile(grid, center, fwhm):
    """Calculate the Lorentzian profile on a given grid centered at 'center'."""
    hwhm = fwhm / 2
    return (1 / np.pi) * (hwhm / ((grid - center)**2 + hwhm**2))

def add_white_noise(spectrum: np.ndarray, num_cycles_per_step: float, is_cavity_mode: bool) -> np.ndarray:
    """
    Adds white noise to the input spectrum.
    """
    if is_cavity_mode:
        noise_level = 0.01 / np.sqrt(num_cycles_per_step)
    else:
        noise_level = 0.05 / np.sqrt(num_cycles_per_step)

    noise = np.random.normal(0, noise_level, spectrum.shape)
    return spectrum + noise

def apply_cavity_mode_response(
    params: dict[str, object],
    frequency_grid: np.ndarray,
    spectrum: np.ndarray,
    v_res: float = 8206.4,
    Q: float = 10000,
    Pmax: float = 1.0
) -> np.ndarray:
    """
    Multiply the spectrum by the cavity mode response
    """
    frequencyMode = params.get("acquisitionType", "single")
    num_cycles_per_step = params.get("numCyclesPerStep", 1)
    
    if frequencyMode == "single":
        # Single cavity mode centered at v_res.
        gamma = v_res / Q
        cavity_response = Pmax * ((gamma / 2) ** 2 / ((frequency_grid - v_res) ** 2 + (gamma / 2) ** 2))
        
    elif frequencyMode == "range":
        # In range mode, we require frequencyMin, frequencyMax, and stepSize.
        frequency_min = params.get("frequencyMin")
        frequency_max = params.get("frequencyMax")
        stepSize = params.get("stepSize")
        if frequency_min is None or frequency_max is None or stepSize is None:
            raise ValueError("For frequency range mode, 'frequencyMin', 'frequencyMax', and 'stepSize' must be provided.")
        
        # Create a list of cavity mode centers, separated by stepSize.
        centers = np.arange(frequency_min, frequency_max + stepSize, stepSize)
        cavity_response = np.zeros_like(frequency_grid)
        for center in centers:
            gamma = center / Q 
            response = Pmax * ((gamma / 2) ** 2 / ((frequency_grid - center) ** 2 + (gamma / 2) ** 2))
            cavity_response += response
    
    # Add white noise to the cavity response.
    cavity_response = add_white_noise(cavity_response, num_cycles_per_step, is_cavity_mode=True)

    # Multiply the original spectrum by the cavity response.
    return spectrum * cavity_response
