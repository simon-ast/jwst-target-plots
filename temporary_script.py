import logging as log
import polars as pl
import numpy as np
import pyvo

# GLOBALS
PS_SELECT = "pl_name, pl_orbper, pl_orbsmax, pl_rade, pl_bmasse, pl_eqt, " \
            "st_teff"


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
    name_sequence = ""
    for name in query_names:
        name_sequence += f"'{name}',"
    name_sequence = name_sequence[:-1]

    # ToDo: Can produce a unique-named list of planetary targets.
    # Next step will be to query the EPA for all necessary parameters
    tap_source = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    service = pyvo.dal.TAPService(tap_source)
    query_string = (f"SELECT {PS_SELECT} FROM pscomppars WHERE "
                    # default_flag = 1 AND "
                    f"pl_name IN ({name_sequence})")
    result_table = service.search(query_string)
    lost_targets = np.setxor1d(query_names, result_table["pl_name"])

    import pandas as pd
    query_result = pl.from_pandas(pd.DataFrame(result_table))

    final = update_frame(polars_frame, query_result)
    print(final)


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

    finalised = pl.DataFrame(dict_name)
    return finalised


def update_rows(row_dict, query_result):
    # print(row_dict)
    # print(query_result.row(by_predicate=(pl.col("pl_name") == row_dict["planet_name"]), named=True))
    try:
        relevant_query = query_result.row(
            by_predicate=(pl.col("pl_name") == row_dict["planet_name"]),
            named=True
        )
        for key, value in relevant_query.items():
            row_dict[key] = value

    except pl.exceptions.NoRowsReturnedError:
        pass

    return row_dict


if __name__ == "__main__":
    main()
