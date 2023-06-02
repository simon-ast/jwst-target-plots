import pyvo
import pandas as pd
import logging as log
import numpy as np

# GLOBALS
PS_SELECT = "pl_name, pl_orbper, pl_orbsmax, pl_rade, pl_bmasse, pl_eqt, " \
            "st_teff"


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
    result_table = service.search(adql_query)

    # Sanity check: No targets are lost in the query (ONLY A WARNING FOR NOW)
    lost_targets = np.setxor1d(target_names, result_table["pl_name"])

    if lost_targets.size == 0:
        log.info("All targets queried successfully!\n")
    else:
        log.info(f"The following {lost_targets.shape[0]} targets could not be "
                 f"queried in the EPA:\n"
                 f"{lost_targets}\n")

    return result_table.to_table().to_pandas()


def construct_adql_query(planet_names: np.ndarray) -> str:
    """Construct a string to query the exoplanet archive through TAP"""
    # Construct correct target name string
    # (and remove the trailing comma from this method)
    name_sequence = ""
    for name in planet_names:
        name_sequence += f"'{name}',"

    # THIS removes the trailing comma
    name_sequence = name_sequence[:-1]

    # Base query: Search in the "planetary system composite"
    # (or pscomppars) table (rather than the ps table)
    base_str = f"SELECT {PS_SELECT} FROM pscomppars "
    query_name = f"WHERE pl_name IN ({name_sequence}) "
    #query_default_values = "AND default_flag = 1"

    return f"{base_str}{query_name}"
