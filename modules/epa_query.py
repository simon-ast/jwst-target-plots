import pyvo
import pandas as pd
import logging as log
import numpy as np

# GLOBALS
QUERY_PARAMETERS = {
    # Auxiliary information
    "pl_name": "planet_name",
    # Orbital period in days
    "pl_orbper": "period_day", "pl_orbper_reflink": "period_ref",
    "pl_orbpererr1": "period_errpos", "pl_orbpererr2": "period_errneg",
    "pl_orbperlim": "period_limit",
    # Semi-major axis in au
    "pl_orbsmax": "sma_au", "pl_orbsmax_reflink": "sma_ref",
    "pl_orbsmaxerr1": "sma_errpos", "pl_orbsmaxerr2": "sma_errneg",
    "pl_orbsmaxlim": "sma_limit",
    # Planet radius in Earth radii
    "pl_rade": "radius_rearth", "pl_rade_reflink": "radius_ref",
    "pl_radeerr1": "radius_errpos", "pl_radeerr2": "radius_errneg",
    "pl_radelim": "radius_limit",
    # Planetary mass in Earth masses (either sin(i) or absolute)
    "pl_bmasse": "mass_mearth", "pl_bmasse_reflink": "mass_ref",
    "pl_bmasseerr1": "mass_errpos", "pl_bmasseerr2": "mass_errneg",
    "pl_bmasselim": "mass_limit",
    # Planetary equilibrium temperature in Kelvin
    "pl_eqt": "eq-temp_kelvin", "pl_eqt_reflink": "eq-temp_ref",
    "pl_eqterr1": "eq-temp_errpos", "pl_eqterr2": "eq-temp_errneg",
    "pl_eqtlim": "eq-temp_limit",
    # Stellar effective temperature in Kelvin
    "st_teff": "star-teff_kelvin", "st_teff_reflink": "star-teff_ref",
    "st_tefferr1": "star-teff_errpos", "st_tefferr2": "star-teff_errneg",
    "st_tefflim": "star-teff_limit",
}


def query_nasa_epa(target_names: np.ndarray) -> pd.DataFrame:
    """
    Query the NASA Exoplanet Archive using TAP through pyVO. The
    values returned here are the ones flagged as "default" in the EPA
    catalogue.
    """
    # Set up NASA EPA query with pyVO
    tap_source = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    service = pyvo.dal.TAPService(tap_source)

    # Construct ADQL query
    log.info(f"Querying NASA EPA for {target_names.shape[0]} targets:\n"
             f"{target_names}\n")
    adql_query = construct_adql_query(target_names)

    # Use pyVO to query NASA EPA
    result_table = service.search(adql_query)  # type: ignore

    # Sanity check: No targets are lost in the query 
    # (ONLY A WARNING FOR NOW)
    lost_targets = np.setxor1d(target_names, result_table["pl_name"])

    if lost_targets.size == 0:
        log.info("All targets queried successfully!\n")
    else:
        log.warning(
            f"The following {lost_targets.shape[0]} target(s) could "
            f"not be queried in the EPA:\n{lost_targets}\n"
        )

    # Make into pandas frame
    pandas_frame = result_table.to_table().to_pandas()
    pandas_frame.rename(columns=QUERY_PARAMETERS, inplace=True)

    return pandas_frame


def construct_adql_query(planet_names: np.ndarray) -> str:
    """Construct a string to query the exoplanet archive through TAP"""
    # Construct correct query-related strings
    selection_string = string_from_list(list(QUERY_PARAMETERS.keys()))
    name_sequence = string_from_list(list(planet_names), "'")

    # Base query: Search in the "planetary system composite"
    # (or pscomppars) table (rather than the ps table)
    base_str = f"SELECT {selection_string} FROM pscomppars "
    query_name = f"WHERE pl_name IN ({name_sequence})"

    # Log information about the queried table
    log.info(
        "All queries are made to the 'pscomppars' table "
        "(https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html) "
        ", which means they might not be entirely self-consistent!\n")

    return f"{base_str}{query_name}"


def string_from_list(names: list, qualifier: str = "") -> str:
    """
    Construct a string of comma-separated values from a list.
    An optional qualifier can be wrapped around list-entries.
    """
    name_sequence = ""
    for name in names:
        name_sequence += f"{qualifier}{name}{qualifier},"

    # THIS removes the trailing comma
    name_sequence = name_sequence[:-1]

    return name_sequence
