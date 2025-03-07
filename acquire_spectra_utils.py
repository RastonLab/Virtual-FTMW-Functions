import os
import numpy as np

def get_datafile(molecule: str, directory: str = "linelists") -> str:
    """
    Return the full path to the data file corresponding to the given molecule.
    The mapping between molecule (chemical formula) and actual data file is defined
    in the dictionary below.
    """
    molecule_to_file = {
        "C7H5N": "benzonitrile.dat",
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
    if len(params) != 6:
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
    ]

    for key, value in params.items():
        if (key not in valid_params) or (params[key] is None):
            print(f"  error with key: {key}. Value is: {value}")
            return False

    return True

def lorentzian_profile(grid, center, hwhm):
    """Calculate the Lorentzian profile on a given grid centered at 'center'."""
    return (1 / np.pi) * (hwhm / ((grid - center)**2 + hwhm**2))

def add_white_noise(spectrum: np.ndarray, num_cycles_per_step: float, is_cavity_mode: bool) -> np.ndarray:
    """
    Adds white noise to the input spectrum.
    """
    if is_cavity_mode:
        noise_level = 0.1 / np.sqrt(num_cycles_per_step)
    else:
        noise_level = 0.002 / np.sqrt(num_cycles_per_step)

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
    # Compute the linewidth Gamma from the Q factor.
    gamma = v_res / Q 

    # Compute P(v) for each frequency point in frequency_grid.
    cavity_response = Pmax * ((gamma/2)**2 / ((frequency_grid - v_res)**2 + (gamma/2)**2))

    # Grab number of cycles per step from params.
    num_cycles_per_step = params.get("numCyclesPerStep")

    # Get white noise for the cavity response.
    cavity_response = add_white_noise(cavity_response, num_cycles_per_step, is_cavity_mode=True)

    # Multiply the original spectrum by the cavity response.
    return spectrum * cavity_response
