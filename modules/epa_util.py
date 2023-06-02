import logging as log
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple


def constrain_plotting_df(
        full_df: pd.DataFrame,
        column_list: list
) -> pd.DataFrame:
    """
    Constraining an input-df based on nan-values in cells, as well as
    only one entry per target and observation type
    """
    # First, drop all entries where the EPA query failed
    epa_sc = full_df.dropna(subset=["pl_name"])

    # Create unique data frame based on target name and observation type
    specialised_df = epa_sc.drop_duplicates(subset=["Target Name", "Type"],
                                            ignore_index=True)

    # Constrain to available values
    constrained_df = specialised_df.dropna(subset=column_list,
                                           ignore_index=True)

    # Check for remaining empty values and log missing targets
    dropped_df = specialised_df.loc[
        pd.isnull(specialised_df[column_list]).any(axis=1)
    ]
    log.info(f"Not plotting "
             f"{np.unique(dropped_df['Target Name'].values)} "
             f"due to missing values!\n")

    return constrained_df


def plot_parameters(
        full_df: pd.DataFrame,
        x_param: str, y_param: str,
        savename: str
) -> None:
    """
    Wrapper for plotting target parameters with variable x- and
    y-parameters
    """
    log.info(f"Plotting {x_param} against {y_param}")

    # SANITY CHECK: x- and y-parameters must be columns in the data frame
    # TO BE ADDED

    # Constraining data frame to usable values
    plotting_df = constrain_plotting_df(full_df, [x_param, y_param])

    # Plot the remaining values
    fig, ax = draw_figure(savename)
    fill_figure(ax, plotting_df, x_param, y_param)
    finish_figure(savename)

    return None


def draw_figure(savename: str) -> Tuple[plt.Figure, plt.Axes]:
    """Instantiate pyplot figure"""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set(title=f"{savename}")
    return fig, ax


def fill_figure(
        ax: plt.Axes, specialised_df: pd.DataFrame,
        x_param: str, y_param: str
) -> None:
    """
    Fill figure with data points. The data frame drawn from here already
    needs to be completely prepared for plotting.
    """
    # ax.scatter(specialised_df[x_param], specialised_df[y_param])

    transits = specialised_df.loc[specialised_df["Type"] == "Transit"]
    eclipses = specialised_df.loc[specialised_df["Type"] == "Eclipse"]

    ax.scatter(transits[x_param], transits[y_param], color="tab:blue",
               marker="o", edgecolor="black")
    ax.scatter(eclipses[x_param], eclipses[y_param], color="tab:red",
               marker=".", edgecolor="black")

    ax.set(xlabel=f"{x_param}", ylabel=f"{y_param}")

    # Potential axis scaling
    if x_param in ["pl_orbper", "pl_orbsmax"]:
        plt.xscale("log")

    return None


def finish_figure(savename: str) -> None:
    """Clean up pyplot figure"""
    plt.tight_layout()
    plt.savefig(f"plots/target_parameters/{savename}.svg")

    return None
