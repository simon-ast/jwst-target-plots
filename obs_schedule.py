"""
OUTLINE:
- Name of target on y-axis
- Date on x-axis
- Instrument as colour-map

TODO:
- Custom legend with instrument color map
"""
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import modules.util as u


# GLOBALS
INPUT_FILE = "data/JWST_cycle1_targets.csv"
INSTRUMENT_COLOUR_MAP = {
    "NIRSpec": "tab:blue", "MIRI": "tab:red",
    "NIRISS": "tab:orange", "NIRCam": "tab:green"
}


def main():
    """Main call"""
    # Read the input file, and explode the observation date column
    # (also convert to datetime objects)
    target_list_all = explode_df_obs_date(
        pd.read_csv(INPUT_FILE), "Observation Date(s) [MM/DD/YY]", ";"
    )

    target_list, final_length = select_targets(
        target_list_all, eap_constraint=0,
        obstype_constr=["Transit"],
        radius_constr=[None, 4]
    )

    # Plotting routine
    fig, ax = timeline_plot_setup()
    for idx in range(final_length):
        indiv_target_plot(target_list.iloc[idx], ax)

    # Plot indication of current date
    today = dt.datetime.today()
    ax.axvline(today, ls="--", c="black")

    # Final steps
    timeline_plot_cleanup(ax)
    plt.savefig(f"plots/timeline_cycle1.svg")


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
    dates = np.array(
        [entry.strip() for entry in new_frame[explode_column].values]
    )
    new_frame[explode_column] = dates

    # Some observations are marked as "Long Range", meaning they are
    # being extended into Cycle 2 due to scheduling
    longrange = new_frame.loc[new_frame[explode_column] == "Long Range"]
    print("\n\n The following entries have been marked as 'Long Range'\n"
          f"{longrange}\n")

    # Remove these from the data frame
    cleaned_frame = new_frame.loc[new_frame[explode_column] != "Long Range"]
    clean_dates = cleaned_frame[explode_column]

    dates_nf = [
        dt.datetime.strptime(d.strip(), '%m/%d/%y').date()
        for d in clean_dates
    ]

    # Replace entries for observation date in new frame
    cleaned_frame[explode_column] = dates_nf

    return cleaned_frame


def select_targets(target_df: pd.DataFrame,
                   eap_constraint=None,
                   instr_constr=None,
                   obstype_constr=None,
                   radius_constr=None):
    """Data filtering for plotting routine"""
    # Select EAP constraint
    if eap_constraint is not None:
        target_df = target_df.loc[
            target_df["EAP [mon]"] <= eap_constraint
        ]

    # Select specific instrument(s)
    # TODO: Fix instrument selection
    #if instr_constr is not None:
    #    reduced_frame = target_df.loc[
    #        target_df["Instrument"].str.split(" / ")[0] in instr_constr
    #    ]

    # Select specific observation type
    if obstype_constr is not None:
        target_df = target_df.loc[
            target_df["Type"].isin(obstype_constr)
        ]

    # Select specific radius values
    if radius_constr is not None:

        # Lower limit
        if radius_constr[0] is not None:
            target_df = target_df.loc[
                radius_constr[0] <= target_df["Radius [RE]"]
            ]

        # Upper limit
        if radius_constr[1] is not None:
            target_df = target_df.loc[
                target_df["Radius [RE]"] <= radius_constr[1]
                ]

    # Also return length of final selection
    entry_length = target_df.shape[0]

    return target_df, entry_length


def assign_inst_colour(raw_data_frame: pd.Series,
                       inst_key: str):
    """Assign colour for plot based on instrument used"""
    # Instrument colour scheme
    inst_col = INSTRUMENT_COLOUR_MAP

    # Target instrument key values
    inst_keys = raw_data_frame[inst_key].split(" / ")

    # Assign colours based on instrument (entries are e.g. "NIRspec, BOTS")
    colour_key = inst_col[inst_keys[0]]

    return colour_key


def indiv_target_plot(df_entry: pd.Series, ax):
    """DOCSTRING!"""
    # Plot parameters
    date = df_entry["Observation Date(s) [MM/DD/YY]"]
    name = df_entry["Target Name"]
    colour_inst = assign_inst_colour(df_entry, "Instrument")

    # Plot values and
    ax.scatter(date, name, c=colour_inst, zorder=4)


def timeline_plot_setup():
    """General plot setup"""
    fig, ax = plt.subplots(figsize=(15, 5))

    # Plot labeling
    ax.set(xlabel="Date", ylabel="Target Name")
    ax.grid(axis="y", zorder=0)

    return fig, ax


def timeline_plot_cleanup(ax):
    """General plot cleanup"""
    # Create and place custom legend
    inst_legend = custom_legend()
    ax.legend(handles=inst_legend, ncols=len(inst_legend))

    # Last adjustments
    plt.gca().invert_yaxis()
    plt.tight_layout()


def custom_legend():
    """Create a custom instrument color legend to include in the plot"""
    handles = list(INSTRUMENT_COLOUR_MAP.keys())
    colours = [INSTRUMENT_COLOUR_MAP[entry] for entry in handles]

    legend_entries = [
        Line2D(
            [0], [0], marker='o', color='w', markersize=10,
            label=f"{handles[i]}", markerfacecolor=f"{colours[i]}")
        for i in range(len(handles))
    ]

    return legend_entries


if __name__ == "__main__":
    # General plot setup
    u.rc_setup()

    # Individual plot parameters
    mpl.rcParams["ytick.right"] = "False"
    mpl.rcParams["ytick.left"] = "False"
    mpl.rcParams["xtick.minor.bottom"] = "False"
    mpl.rcParams["xtick.minor.top"] = "False"
    mpl.rcParams["legend.frameon"] = "True"
    mpl.rcParams["legend.framealpha"] = 1.0

    print("\n\n REVISE OBS DATE ENTRIES! \n\n")
    main()
