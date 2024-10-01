import logging as log
import polars as pl
import numpy as np
import pyvo

import modules.epa_query as epa


# GLOBALS
PS_SELECT = "pl_name, pl_orbper, pl_orbsmax, pl_rade, pl_bmasse, pl_eqt, " \
            "st_teff"

QUERY_PARAMETERS = {
    "pl_name": "planet_name",
    "pl_orbper": "period_day",
    "pl_orbsmax": "sma_au",
    "pl_rade": "radius_rearth",
    "pl_bmasse": "mass_mearth",
    "pl_eqt": "eq-temp_kelvin",
    "st_teff": "st-teff_kelvin"
}


def main():
    # ToDO: Update logging config (filename)
    log.basicConfig(
        filename="test_run.log",
        filemode="w",
        format='%(name)s - %(levelname)s - %(message)s',
        level=log.INFO
    )

    # Test-read of file
    filename = "data/JWST_targets_new_test.csv"
    polars_frame = pl.read_csv(filename)
    tot_num_planets, _ = polars_frame.shape

    # Redo this with proper function
    cycle_indicator = pl.Series(
        "jwst_cycle", np.full(tot_num_planets, 1, dtype=int)
    )
    # ToDo: Why is the the second to last, not the last column?
    polars_frame.insert_column(-1, cycle_indicator)

    # Make unique name series
    unique_names = polars_frame.unique(
        subset=["host_name", "planet_id"],
        maintain_order=True
    )
    query_names = unique_names["planet_name"].to_numpy()
    query_result = pl.from_pandas(epa.query_nasa_epa(query_names))

    final = update_frame(polars_frame, query_result)

    final.write_csv(file="test.csv")
    save_reduced_frame(final)


def update_frame(parent_frame, child_frame):

    queried_columns = np.setdiff1d(
        child_frame.columns, parent_frame.columns
    )

    final_frame = parent_frame.with_columns([
        pl.lit(np.nan).alias(column_name)
        for column_name in queried_columns
    ])

    dict_name = [
        update_rows(element, child_frame)
        for element in final_frame.iter_rows(named=True)
    ]

    finalised = pl.DataFrame(dict_name).sort(by="planet_name")
    return finalised


def update_rows(row_dict, query_result):
    try:
        relevant_query = query_result.row(
            by_predicate=(pl.col("planet_name") == row_dict["planet_name"]),
            named=True
        )
        for key, value in relevant_query.items():
            row_dict[key] = value

    except pl.exceptions.NoRowsReturnedError:
        # This skips over failed queries (which are noted in the log-file)
        pass

    return row_dict


def save_reduced_frame(
        total_frame: pl.DataFrame
        ) -> None:
    "Save a reduced version of the full query frame."
    intial_parameters = [
        "planet_name", "jwst_instrument", "jwst_filter", "jwst_dispersion",
        "type", "num_obs", "jwst_cycle", "pid", "eap_months"
    ]
    reduced_parameters = [
        "radius_rearth", "mass_mearth", "period_day", "sma_au",
        "eq-temp_kelvin", "host_name", "star-teff_kelvin"
    ]
    selection = intial_parameters + reduced_parameters

    # Save a reduced frame
    total_frame[selection].write_csv("test_reduced.csv")

    return None


if __name__ == "__main__":
    main()
