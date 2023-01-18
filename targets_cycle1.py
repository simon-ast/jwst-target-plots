import matplotlib.pyplot as plt
import modules.util as u
import modules.plotting as p

# GLOBALS
INPUT_DATA = "data/cycle1_targets.csv"
PLOT_DIR = "plots/"


def main():
    """
    Generates plots for Cycle 1 GO/GTO/DD-ERS targets and HD260655 b/c.
    """
    # Potential cycle 2 target(s) of HD 260655 + Mercury data
    c2_target = u.cycle2_proposal("data/cycle2_target.txt")

    # Selection of cycle 1 sub-Neptune targets
    target_list = u.dict_cycle1_targets(INPUT_DATA)
    transit_targets = u.cycle1_selection(target_list, "Transit")
    eclipse_targets = u.cycle1_selection(target_list, "Eclipse")

    data_set = u.combine_transit_eclipse(transit_targets, eclipse_targets)

    # Plotting cycle 1 targets, potential new target and HZ
    u.rc_setup()
    fig, ax = p.plot_backdrop()
    p.plot_target_list(data_set, fig, ax)

    # Proposal target and mercury parameters
    ax.scatter(c2_target["sma"], c2_target["Teff"], c=c2_target["Teq"],
               vmin=100, vmax=2000, cmap=plt.cm.get_cmap('RdYlBu').reversed(),
               edgecolor="black")

    ax.scatter(0.387, 5773, c="black", marker="P")

    plt.legend(framealpha=0.)
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/cycle1_targets.pdf")


if __name__ == "__main__":
    main()
