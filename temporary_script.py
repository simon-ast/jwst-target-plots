import logging as log
import polars as pl
import numpy as np
import pyvo


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
    query_names = unique_names["planet_name"]
    print(query_names.to_numpy())

    # ToDo: Can produce a unique-named list of planetary targets.
    # Next step will be to query the EPA for all necessary parameters


if __name__ == "__main__":
    main()
