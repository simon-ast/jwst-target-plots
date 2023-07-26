import pandas as pd
import numpy as np
import astropy.constants as c


def kempton_tsm(eqt: pd.DataFrame) -> pd.Series:
    """
    Calculate the TSM value as described in Kempton et al. (2018)
    """
    # Correct values for T_eq
    t_eq_kempton = kempton_teq(eqt)
    eqt["pl_eqt"].fillna(t_eq_kempton, inplace=True)
    t_eq = eqt["pl_eqt"]

    # Split up the calculation
    enum = (eqt["pl_rade"]) ** 3 * t_eq
    denom = (eqt["pl_masse"] * eqt["st_rad"] ** 2)
    factor = 10 ** (- eqt["sy_jmag"] / 5)

    # Scale factor assignment
    scale_factor = np.array(
        [kempton_scale_factor(radius) for radius in eqt["pl_rade"]]
    )

    # Put everything together to calculate TSM
    tsm = scale_factor * enum / denom * factor

    # Return the TSM as a rounded integer
    return np.round(tsm)


def kempton_teq(eqt: pd.DataFrame) -> pd.Series:
    """
    Assignment of equilibrium temperature according to Kempton et al. (2018)
    """
    t_eq = eqt["st_teff"] * np.sqrt(
        (eqt["st_rad"] * c.R_sun) / (eqt["pl_orbsmax"] * c.au)
    ) * (1/4) ** (1/4)

    return t_eq


def kempton_scale_factor(pl_rad):
    """Assign a scale-factor to each planet following Table 1"""
    scale_factors = [0.190, 1.26, 1.28, 1.15]

    if pl_rad <= 1.5:
        return scale_factors[0]

    elif pl_rad <= 2.75:
        return scale_factors[1]

    elif pl_rad <= 4.0:
        return scale_factors[2]

    elif pl_rad <= 10.0:
        return scale_factors[3]

    else:
        return scale_factors[3]
        # This should not be able to trigger when only querying sub-Neptunes
    #    print("WHAT?")


def atmospheric_signal(mmw: float, result_df: pd.DataFrame) -> pd.Series:
    """
    Calculate transit depth modulation in ppm, based on 5 scale heights
    """
    # First, calculate scale height of the atmosphere
    scale_h = calc_scale_height(mmw, result_df)

    # Following Tinetti et al. (2013), equation 1, the zeroth-order
    # approximation of the atmospheric signal from 5 scale heights
    enum = 2 * result_df["pl_rade"] * c.R_earth * scale_h
    denom = (result_df["st_rad"] * c.R_sun) ** 2

    # Result in ppm
    signal = 5 * enum / denom * 1e6

    return np.round(signal)


def calc_scale_height(mmw: float, result_table: pd.DataFrame) -> pd.Series:
    """
    Calculate scale height estimate (using equilibrium-temperature
    values from the NASA EPA right now, rather than the calculation
    routine described in Kempton et al. (2018))
    """
    # Should I use this instead?
    # teq = kempton_teq(result_table)

    teq = result_table["pl_eqt"]
    grav_g = calc_grav_g(result_table["pl_masse"], result_table["pl_rade"])

    scale_h = c.k_B * teq / (grav_g * mmw * c.u)

    return scale_h


def calc_grav_g(planet_mass: pd.Series, planet_radius: pd.Series) -> pd.Series:
    """
    Calculate gravitational acceleration in SI-units. Input must be in
    Earth-scaled units
    """
    enum = c.G * planet_mass * c.M_earth
    denom = (planet_radius * c.R_earth) ** 2

    grav_g = enum / denom
    return grav_g


def transit_estimations(result_table: pd.DataFrame) -> None:
    """
    Add some transit markers (total depth, potential relative depth) to
    the result table. Using the 5 * scale-height estimate for now
    """
    # Absolute transit depth in percent
    rp_rs = ((result_table["pl_rade"] * c.R_earth)
             / (result_table["st_rad"] * c.R_sun)) ** 2
    result_table["td_perc"] = rp_rs * 1e2

    # Expected signal for a H2/He-dominated atmosphere (mu_1) and an
    # Earth-like atmosphere (mu_2)
    mu1, mu2 = 2, 25
    result_table["sig_prim_ppm"] = atmospheric_signal(mu1, result_table)
    result_table["sig_seco_ppm"] = atmospheric_signal(mu2, result_table)

    return None
