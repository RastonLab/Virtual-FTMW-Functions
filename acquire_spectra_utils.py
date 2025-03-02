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