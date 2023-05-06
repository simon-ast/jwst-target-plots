import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import pandas as pd
import modules.util as u
import modules.plotting as p

# GLOBALS
INPUT_DATA = "data/JWST_cycle1_targets.csv"
PLOT_DIR = "plots/"
LABEL_ADD = "Transit Targets"


def main():
    """
    Generates plots for Cycle 1 GO/GTO/DD-ERS targets.
    """
    # Selection of cycle 1 targets
    target_list = pd.read_csv(INPUT_DATA)
    transit_targets_all = u.cycle1_selection(target_list, "Transit")
    transit_targets_free = transit_targets_all.loc[
        transit_targets_all["EAP [mon]"] == 0
    ]

    # Plotting cycle 1 targets, HZ sketches and Mercury
    fig1, ax1 = p.plot_backdrop(hz_indicator="dashed")
    p.plot_target_list(transit_targets_all, fig1, ax1)


    # Custom legend
    labels, handles = custom_legend(ax1)
    plt.legend(labels=labels, handles=handles, framealpha=0.)
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/cycle1_targets_et.svg")

    # Same as above, but with EAPs overplotted
    fig2, ax2 = p.plot_backdrop(hz_indicator="dashed")
    p.plot_target_list(transit_targets_all, fig2, ax2)
    restricted_tar = transit_targets_all.loc[
        transit_targets_all["EAP [mon]"] != 0
    ]
    ax2.scatter(restricted_tar["SMA [au]"], restricted_tar["Teff [K]"],
                color="tab:red", marker="x", lw=2.5)
    labels, handles = custom_legend(ax2)
    plt.legend(labels=labels, handles=handles, framealpha=0.)
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/cycle1_targets_eap.svg")

    # Only targets without EAPs
    fig3, ax3 = p.plot_backdrop(hz_indicator="dashed")
    p.plot_target_list(transit_targets_free, fig3, ax3)
    labels, handles = custom_legend(ax3)
    plt.legend(labels=labels, handles=handles, framealpha=0.)
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/cycle1_targets_free.svg")
    print(f"{len(transit_targets_free)} transit targets in this list!\n")


def custom_legend(ax):
    # Custom legend
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Line2D([0], [0], marker='o', color='w', mfc='black'))
    labels.append(LABEL_ADD)

    return labels, handles


if __name__ == "__main__":
    u.rc_setup()
    main()
