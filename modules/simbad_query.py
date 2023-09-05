from astroquery.simbad import Simbad
from typing import Union
import pandas as pd
import numpy as np


def query_simbad_names(name_list: Union[np.ndarray, list]) -> np.ndarray:
    """
    Simple SIMBAD query to unify naming-convention when comparing lists
    """
    result_table = Simbad.query_objects(name_list)

    return np.array(result_table["MAIN_ID"], dtype=str)


def read_targets(file_name: str, column_name: str):
    """
    Simple routine extracting a single column from a pandas-read csv-file
    """
    full_frame = pd.read_csv(f"data/{file_name}")
    col_of_interest = full_frame[column_name].to_numpy()

    return col_of_interest


def target_comparison(raw_query: pd.DataFrame) -> None:
    """
    Compares names in the EPA query list with the ARIEL T2 target list
    from Billy Edwards, and with my own JWST target lists.
    """
    # Insert ARIEL and JWST column
    raw_query["ARIEL"] = None
    raw_query["JWST"] = None
    
    # Comparison libraries
    ariel = read_targets("ArielT2MCS_11Apr2023.csv", "Planet Name")
    jwst_cycle1 = read_targets("JWST_cycle1_targets.csv", "Target Name")
    jwst_cycle2 = read_targets("JWST_cycle2_targets.csv", "Target Name")
    jwst = np.unique(np.append(jwst_cycle1, jwst_cycle2))

    # Query SIMBAD for common names (and hold for arbitrary amount of
    # time, to make sure queries are finished)
    ariel_simbad = query_simbad_names(ariel)
    jwst_simbad = query_simbad_names(jwst)

    for planet in raw_query["pl_name"]:
        try:
            unique_id = np.array(
                Simbad.query_objects([planet])["MAIN_ID"], dtype=str
            )
        except TypeError:
            # This step supplements the initial name from the JWST or
            # Ariel files into the comparison, just in case they match
            # up (without first unifying them through SIMBAD). This
            # will work e.g. for the TrES-planets
            unique_id = planet

        if unique_id in ariel or unique_id in ariel_simbad:
            raw_query.loc[raw_query["pl_name"] == planet, "ARIEL"] = True

        if unique_id in jwst or unique_id in jwst_simbad:
            raw_query.loc[raw_query["pl_name"] == planet, "JWST"] = True

    return None
