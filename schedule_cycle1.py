"""
OUTLINE:
- Name of target on y-axis
- Date on x-axis
- Instrument as colour-map
"""
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import modules.util as u


# GLOBALS
INPUT_FILE = "data/JWST_cycle1_targets.csv"


def main():
    """Main call"""
    # Read the input file, and explode the observation date column
    # (also convert to datetime objects)
    target_list_all = explode_df_obs_date(
        pd.read_csv(INPUT_FILE), "Observation Date(s) [MM/DD/YY]", ";"
    )

    # TODO: Entry sorting (Transit, EAP, Radius)
    target_list = target_list_all.loc[
        target_list_all["EAP [mon]"] == 0
    ]

    # TODO: External plotting routine, clean-up, saving figure
    plt.scatter(target_list["Observation Date(s) [MM/DD/YY]"],
                target_list["Target Name"],
                c=assign_inst_colour(target_list, "Instrument"))

    plt.tight_layout()
    plt.show()


def explode_df_obs_date(raw_data_frame: pd.DataFrame,
                        explode_column: str,
                        date_delimiter: str) -> pd.DataFrame:
    """Prepare data frame by exploding observation date lists"""
    # Make sure that the date entries in the data frame are lists by
    # using string-split method with a pre-defined delimiter
    raw_data_frame[explode_column] = \
        raw_data_frame[explode_column].str.split(date_delimiter)

    # Generate a new data frame by exploding the observation date lists
    new_frame = raw_data_frame.explode(explode_column, ignore_index=True)

    # Generate individual Series (assuming exploding column is date!)
    dates = new_frame[explode_column].values
    dates_nf = [dt.datetime.strptime(d.strip(), '%m/%d/%y').date()
                for d in dates]

    # Replace entries for observation date in new frame
    new_frame[explode_column] = dates_nf

    return new_frame


def assign_inst_colour(raw_data_frame: pd.DataFrame,
                       inst_key: str):
    """DOC!"""
    # Instrument colour scheme
    inst_col = {"NIRSpec": "tab:blue", "MIRI":"tab:red",
                "NIRISS": "tab:orange", "NIRCam": "tab:green"}

    # Target instrument key values
    inst_keys = raw_data_frame[inst_key].str.split(" / ").values

    # Assign colours based on instrument (entries are e.g. "NIRspec, BOTS")
    colour_keys = [inst_col[instrument[0]] for instrument in inst_keys]

    return colour_keys


if __name__ == "__main__":
    u.rc_setup()
    print("\n\n REVISE OBS DATE ENTRIES! \n\n")
    main()
