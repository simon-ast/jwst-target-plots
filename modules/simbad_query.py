import pandas as pd
from astroquery.simbad import Simbad
import numpy as np
from typing import Union


def query_simbad_names(name_list: Union[np.ndarray, list]) -> np.ndarray:
    """
    Simple SIMBAD query to unify naming-convention when comparing lists
    """
    result_table = Simbad.query_objects(name_list)

    return np.array(result_table["MAIN_ID"], dtype=str)


def target_comparison(raw_query: pd.DataFrame) -> None:
    """
    Compares names in the EPA query list with the ARIEL T2 target list
    from Billy Edwards, and with my own JWST target lists
    """
    # Comparison libraries
    ariel = pd.read_csv(
        "data/ArielT2MCS_11Apr2023.csv"
    )["Planet Name"].to_numpy()
    ariel_simbad = query_simbad_names(ariel)

    jwst_cycle1 = pd.read_csv("data/JWST_cycle1_targets.csv"
                              )["Target Name"].to_numpy()
    jwst_cycle2 = pd.read_csv("data/JWST_cycle2_targets.csv"
                              )["Target Name"].to_numpy()
    jwst = np.unique(np.append(jwst_cycle1, jwst_cycle2))
    jwst_simbad = query_simbad_names(jwst)

    for planet in raw_query["pl_name"]:
        try:
            unique_id = np.array(
                Simbad.query_objects([planet])["MAIN_ID"], dtype=str
            )
        except TypeError:
            unique_id = planet

        if unique_id in ariel or unique_id in ariel_simbad:
            raw_query.loc[raw_query["pl_name"] == planet, "ARIEL"] = True

        if unique_id in jwst or unique_id in jwst_simbad:
            raw_query.loc[raw_query["pl_name"] == planet, "JWST"] = True

    return None
