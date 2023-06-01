import matplotlib.pyplot as plt
import modules.epa_query as eq
import modules.epa_util as eu
import logging as log
import sys
import numpy as np
import pandas as pd
import copy as cp
import modules.util as u

# GLOBALS
DATA_DIR = "data"
X_AXIS = "pl_orbsmax"
Y_AXIS = "st_teff"


def main():
    # Set up logging solution
    log.basicConfig(filename=f'output/{sys.argv[0][:-3]}.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=log.INFO)

    # Reading in the csv-list information
    file_nc1 = "JWST_cycle1_targets.csv"
    cycle1 = read_target_csv(DATA_DIR, file_nc1)
    file_nc2 = "JWST_cycle2_targets.csv"
    cycle2 = read_target_csv(DATA_DIR, file_nc2)
    csv_combination = join_df([cycle1, cycle2])

    # Querying the NASA EPA with target names from the csv list
    csv_name = pd.unique(csv_combination["Target Name"])
    epa_queried = eq.query_nasa_epa(csv_name)

    # Concatenate csv and epa results (and save df for posterity)
    constructed = construct_new_df(csv_combination, epa_queried)
    constructed.to_csv("output/epa_correlation.csv", sep="\t")

    # Maybe further restrictions?
    final = constructed
    #final = constructed.loc[constructed["Type"] == "Transit"]

    # PLOT RESULTS
    # Sub-neptunes
    log.info("SUB-NEPTUNES")
    sn_df = final.loc[final["pl_rade"] <= 4.]
    eu.plot_parameters(sn_df, x_param=X_AXIS, y_param=Y_AXIS,
                       savename="subneptunes")

    # HJ and SHJ
    log.info("SUPER-NEPTUNES")
    hj_df = final.loc[final["pl_rade"] > 4.]
    eu.plot_parameters(hj_df, x_param=X_AXIS, y_param=Y_AXIS,
                       savename="superneptunes")


def read_target_csv(data_dir: str, filename: str) -> pd.DataFrame:
    """
    Reads in the csv-file of JWST targets as a pandas-dataframe. Also
    adds a (for now) empty column to store the corresponding SIMBAD ID.
    """
    target_data_frame = pd.read_csv(f"{data_dir}/{filename}")

    # SIMBAD is not used for now
    # target_data_frame["simbad_id"] = np.nan

    return target_data_frame


def join_df(df_list: list[pd.DataFrame]) -> pd.DataFrame:
    """Join multiple data frames containing observational information"""
    joined_df = pd.concat(df_list, ignore_index=True)

    return joined_df


def construct_new_df(
        csv_df: pd.DataFrame,
        epa_df: pd.DataFrame
) -> pd.DataFrame:
    """Concatenate data frames from csv file and EPA query"""
    # Instantiate the new data frame taking necessary values from the
    # csv-file and appending empty columns with names from the EPA
    # data frame
    new_df = cp.deepcopy(csv_df[["Target Name", "Instrument", "Type"]])
    epa_cols = epa_df.columns
    for column in epa_cols:
        new_df[column] = np.nan

    # Fill in the new data frame by using the values from the EPA
    for idx in range(epa_df.shape[0]):
        # EPA query list will give only one planet per row
        epa_subframe = epa_df.iloc[idx]

        # Match with row indices from the csv data frame
        csv_idxs = new_df.loc[
            new_df["Target Name"] == epa_subframe["pl_name"]
        ].index.to_list()

        # Fill in queries values (and DON'T use chained indexing)
        for match_idx in csv_idxs:
            for column in epa_cols:
                # Use "at" to actually assign cell with mixed indexing
                new_df.at[match_idx, column] = epa_subframe.loc[column]

    return new_df


if __name__ == "__main__":
    u.rc_setup()
    main()
    plt.show()
