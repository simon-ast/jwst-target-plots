import numpy as np
import matplotlib.pyplot as plt
import modules.util as u
import modules.plotting as p

# GLOBALS
INPUT_DATA = "data/JWST_Cycle1_Targets.csv"
PLOT_DIR = "plots/"


def main():
    """
    Generates plots for Cycle 1 GO/GTO/DD-ERS targets and HD260655 b/c.
    """
    # Potential cycle 2 target(s) of HD 260655
    c2_target = u.cycle2_proposal("data/cycle2_target.txt")

    # Selection of cycle 1 sub-Neptune targets
    target_list = u.dict_cycle1_targets(INPUT_DATA)
    u.reduced_cycle1_tar(target_list)

    # Plotting cycle 1 targets, potential new target and HZ
    u.rc_setup()
    _, ax = p.plot_target_list(target_list)

    ax.scatter(c2_target["sma"], c2_target["Teff"], c="red")

    plt.savefig(f"{PLOT_DIR}/cycle1_targets.pdf")


if __name__ == "__main__":
    main()
