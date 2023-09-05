import matplotlib.pyplot as plt
import modules.epa_query as eq
import modules.epa_util as eu
import modules.epa_custom_plots as ec
import logging as log
import sys
from typing import Union
import numpy as np
import pandas as pd
import copy as cp
import modules.util as u

# GLOBALS
DATA_DIR = "data"
QUERY = False


def main():
    # Set up logging solution
    log.basicConfig(
        filename=f'output/target_parameters/{sys.argv[0][:-3]}.log',
        filemode='w',
        format='%(name)s - %(levelname)s - %(message)s',
        level=log.INFO
    )

    # Re-query only if necessary
    if QUERY is True:
        print("\nFresh query to NASA EPA\n")

        # Reading in the csv-list information
        csv_combination = read_cycles_info()

        # Querying the NASA EPA with target names from the csv list
        constructed = epa_correlation(csv_combination)

    else:
        print("\n Using existing query results!\n")
        constructed = pd.read_csv(
            "output/target_parameters/epa_correlation.csv", sep="\t"
        )

    # Maybe further restrictions?
    finalised_frame = constructed
    #finalised_frame = constructed.loc[constructed["Type"] == "Transit"]

    # PLOT RESULTS
    specialised_plot(finalised_frame, "all-types")


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
    new_df = cp.deepcopy(csv_df[[
        "Target Name", "Instrument", "Type", "ObsCycle", "EAP [mon]"
    ]])
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


def read_cycles_info() -> pd.DataFrame:
    """
    Hard-coded read-function for observational cycle target information
    """
    file_nc1 = "JWST_cycle1_targets.csv"
    cycle1 = read_target_csv(DATA_DIR, file_nc1)
    cycle1["ObsCycle"] = "Cycle 1"
    file_nc2 = "JWST_cycle2_targets.csv"
    cycle2 = read_target_csv(DATA_DIR, file_nc2)
    cycle2["ObsCycle"] = "Cycle 2"
    combination = join_df([cycle1, cycle2])

    return combination


def epa_correlation(compiled_data: pd.DataFrame) -> pd.DataFrame:
    """Substitute target data with query to NASA EPA"""
    # Querying the NASA EPA with target names from the csv list
    csv_name = pd.unique(compiled_data["Target Name"])
    epa_queried = eq.query_nasa_epa(csv_name)

    # Concatenate csv and epa results (and save df for posterity)
    constructed_frame = construct_new_df(compiled_data, epa_queried)
    constructed_frame.to_csv(
        "output/target_parameters/epa_correlation.csv", sep="\t",
        index=False
    )

    return constructed_frame


def parameter_plot_setup():
    """Set up specialised plot"""
    figure, axis = plt.subplots()

    axis.set(
        xlabel="$R_\\mathrm{p}$ [$R_\\oplus$]", xscale="log",
        ylabel="$P$ [d]", yscale="log"
    )

    return figure, axis


def parameter_plot_fill(
        axis: plt.Axes, data_set: pd.DataFrame,
        colour: Union[str, np.ndarray], opacity=1.0, mec=None
) -> None:
    """Fill axis-object with specified data set"""
    plot = axis.scatter(
        data_set["pl_rade"], data_set["pl_orbper"],
        c=colour, alpha=opacity, edgecolor=mec
    )

    # Insert a colour-bar when necessary
    if isinstance(colour, np.ndarray):
        plt.colorbar(plot, label="$T_\\mathrm{eff}$ [K]")


def specialised_plot(total_df: pd.DataFrame, savename: str):
    """Specialised plot wrapper"""
    # Split into sub-Neptunes and rest
    not_interest = total_df.loc[total_df["pl_rade"] > 4.0].drop_duplicates(
        subset=["pl_name"]
    )
    of_interest = total_df.loc[total_df["pl_rade"] <= 4.0].drop_duplicates(
        subset=["pl_name"]
    )

    # Set up the figure environment
    fig, ax = parameter_plot_setup()

    # Iteratively fill the figure
    parameter_plot_fill(ax, not_interest, "grey", opacity=0.4)
    parameter_plot_fill(
        ax, of_interest, of_interest["st_teff"].to_numpy(), mec="black"
    )

    plt.tight_layout()
    full_save_name = f"target_parameters_{savename}.svg"
    plt.savefig(f"output/target_parameters/{full_save_name}")


if __name__ == "__main__":
    u.rc_setup()
    main()
