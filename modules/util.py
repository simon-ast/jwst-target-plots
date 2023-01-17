import numpy as np
import matplotlib as mpl
from typing import Union


def rc_setup():
    """Generalized plot attributes"""
    mpl.rcParams["xtick.direction"] = "in"
    mpl.rcParams["xtick.labelsize"] = "large"
    mpl.rcParams["xtick.major.width"] = 1.5
    mpl.rcParams["xtick.minor.width"] = 1.5
    mpl.rcParams["xtick.minor.visible"] = "True"
    mpl.rcParams["xtick.top"] = "True"

    mpl.rcParams["ytick.direction"] = "in"
    mpl.rcParams["ytick.labelsize"] = "large"
    mpl.rcParams["ytick.major.width"] = 1.5
    mpl.rcParams["ytick.minor.width"] = 1.5
    mpl.rcParams["ytick.minor.visible"] = "True"
    mpl.rcParams["ytick.right"] = "True"

    mpl.rcParams["axes.linewidth"] = 1.5
    mpl.rcParams["axes.labelsize"] = "large"


def cycle2_proposal(filename: str) -> dict:
    """
    Generates HD260655 b and c parameters, taken from the NASA exoplanet
    archive. Data file is stored in 'data/'
    """
    data = np.genfromtxt(filename, dtype=str, delimiter="\t", skip_header=1)

    # Split the data and turn into dictionary
    return {
        "name": data[:, 0],
        "Mass [Me]": np.array(data[:, 1], dtype=float),
        "Radius [Re]": np.array(data[:, 2], dtype=float),
        "Teff": np.array(data[:, 3], dtype=float),
        "log(L)": np.array(data[:, 4], dtype=float),
        "sma": np.array(data[:, 5], dtype=float)
    }


def dict_cycle1_targets(filename: str) -> dict:
    """
    Generates a keyed dictionary from the .csv file containing all
    targets from cycle 1 GO/GTO/DD-ERS. This can be reduced by e.g.
    planetary radius later on.
    """
    # Read file
    full_array = np.genfromtxt(filename, dtype=str, delimiter=",")
    column_number = len(full_array[0])

    # Fill up empty array spots
    for i in range(len(full_array)):
        full_array[i] = fill_arr(full_array[i], 0.)

    # First array element is list of headers
    headers = full_array[0]
    values = np.transpose(full_array[1:])

    # Create dictionary
    target_set = {headers[i]: values[i] for i in range(column_number)}

    # Make all numbers value arrays into float arrays
    for key in target_set.keys():
        if key != "EAP [mon]":
            try:
                target_set[key] = np.array(target_set[key], dtype=float)
            except ValueError:
                pass

    return target_set


def reduced_cycle1_tar(target_list: dict) -> None:
    """
    Changes the dictionary target list of JWST cycle 1 targets by
    throwing out:
        1. Non-transit observations
        2. Duplicate entries
        3. Targets with missing values (this is why GJ 4102 b is missing)
        4. Only including sub-Neptune sized planets (<= 4 R_e)
    """
    # Sort for Transit Observations. Do this first, as making the
    # dictionary unique might remove transit observations and leave e.g.
    # eclipse observations of the same planet
    ind_transit = np.where(target_list["Type"] == "Transit")
    red_total_dict(target_list, ind_transit)

    # Make dictionary with unique entries (planets)
    make_dict_unique(target_list)

    # Filter out non-available entries
    check_nans(target_list)

    # Sort for super-Earths and mini-Neptunes
    ind_upperrad = np.where(target_list["Radius [RE]"] <= 4.)[0]
    red_total_dict(target_list, ind_upperrad)

    ind_lowerrad = np.where(target_list["Radius [RE]"] > 0.)[0]
    red_total_dict(target_list, ind_lowerrad)

    return None


'''
This is not used for now!

def dict_cycle2_targets(filename):
    """DOC!"""
    # Read as pandas data frame
    data = pd.read_csv(filename, delimiter=",")

    # Fill empty values with 0
    data.fillna(0, inplace=True)

    # Create additional column with planet name
    data["planet_name"] = data["star"] + data["planet"]

    return data
'''


def fill_arr(str_array: np.array, filler: Union[str, float, int]):
    """
    Helper function: fills empty entries in array with predefined filler
    value.
    """
    for i in range(len(str_array)):
        if str_array[i] == "":
            str_array[i] = filler

    return str_array


def red_total_dict(target_dict: dict, index_list: np.array) -> dict:
    """
    Reduces all keyed entries of a dictionary by a given index list.
    """
    dict_keys = list(target_dict.keys())

    # Reduce all dictionary entries
    for key in dict_keys:
        target_dict[key] = target_dict[key][index_list]

    return target_dict


def make_dict_unique(target_dict: dict) -> dict:
    """
    Reduces a given dictionary by duplicate entries, looping through all
     dictionary keys.
     """
    dict_keys = list(target_dict.keys())

    # Find unique indices by target name (first key)
    _, u_indices = np.unique(target_dict[dict_keys[0]], return_index=True)

    # Reduce all dictionary entries
    for key in dict_keys:
        target_dict[key] = target_dict[key][u_indices]

    return target_dict


def check_nans(target_dict: dict) -> dict:
    """Reduces a given dictionary by NaN-entries."""
    dict_keys = list(target_dict.keys())

    by_column = [list(np.where(target_dict[key] != 0.)[0])
                 for key in dict_keys]
    nan_ind = np.unique(np.array(sum(by_column, [])))

    # Reduce all dictionary entries
    for key in dict_keys:
        target_dict[key] = target_dict[key][nan_ind]

    return target_dict


def plotable_hz_bounds(temp=np.linspace(2600, 7200, 5000),
                       lbol=np.linspace(0.01, 1, 5000)) -> dict:
    """Returns a dictionary of inner and outer HZ boundary distances."""
    bounds = ["oi", "ci", "co", "oo"]
    hz_bounds = {
        key: habitable_zone_distance(temp, lbol, key)
        for key in bounds
    }

    return hz_bounds


def habitable_zone_distance(effect_temp, lum, est_ident):
    """
    HZ estimation from Kopparapu et al. (2013, 2014).

    :param effect_temp: NDARRAY, Stellar temperature in Kelvin
    :param lum: NDARRAY, Stellar bolometric luminosity in solar units
    :param est_ident: STR, Identifier for the estimation boundary

    :return: NDARRAY, HZ distance in AU
    """

    # Determine valid indicators
    valid_ind = ["oi", "ci", "co", "oo"]
    est_indices = dict(zip(valid_ind, range(4)))

    # SANITY CHECK: indicator for estimate must exist
    assert est_ident.lower() in ["oi", "ci", "co", "oo"], \
        f"INDICATOR {est_ident} FOR ESTIMATION METHOD NOT RECOGNIZED!"

    # Parameter matrix organized by oi, ci, co, oo estimates
    # PLEASE NOTE THE ERRATUM TO THE ORIGINAL KOPPARAPU (2013) PAPER!
    param = np.array([
        [1.4335e-4, 3.3954e-9, -7.6364e-12, -1.1950e-15],
        [1.2456e-4, 1.4612e-8, -7.6345e-12, -1.7511e-15],
        [5.9578e-5, 1.6707e-9, -3.0058e-12, -5.1925e-16],
        [5.4471e-5, 1.5275e-9, -2.1709e-12, -3.8282e-16],
    ])

    # Set correct param-subindex according to est_ident
    est_index = est_indices[est_ident]

    # Call the S_eff calculation function with correct parameters
    s_eff = effective_flux(param[est_index], effect_temp, est_index)

    # Calculate distance
    distance = np.sqrt(lum / s_eff)

    return distance


def effective_flux(param_list, effect_temp, estimation_index):
    """Intermediate step in HZ calculation"""
    s_effsun = [1.7763, 1.0385, 0.3507, 0.3207]

    # Temperature array consisting of powers 1 to 4
    temp = np.array(
        [(effect_temp - 5780) ** (i + 1) for i in range(4)]
    )

    # Transpose the temperature-power array to have each row be a list
    # of Temp ** 1 to Temp ** 4, and then calculate the dot-product
    # with the parameter list vector
    return s_effsun[estimation_index] + temp.T @ param_list
