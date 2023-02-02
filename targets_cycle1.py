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
    fig, ax = p.plot_backdrop(hz_indicator="dashed")
    p.plot_target_list(data_set, fig, ax)

    # Proposal target and mercury parameters
    # TODO: Annotations for HD System targets
    ax.scatter(c2_target["sma"], c2_target["Teff"], c=c2_target["Teq"],
               vmin=100, vmax=2000, cmap=plt.cm.get_cmap('RdYlBu').reversed(),
               edgecolor="black")

    # Annotations
    x_s, y_s = (c2_target["sma"][0], c2_target["Teff"][0])
    ax.annotate("HD 260655", (x_s, y_s * 1.05))

    planet = ["b", "c"]
    for i in range(2):
        x, y = (c2_target["sma"][i], c2_target["Teff"][i])
        ax.annotate(planet[i], (x * 1.065, y * 1.015))

    ax.scatter(0.387, 5773, c="black", marker="P")

    plt.legend(framealpha=0.)
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/cycle1_targets.png", dpi=600)


if __name__ == "__main__":
    main()
