import numpy as np
import matplotlib.pyplot as plt
import util as u
import plotting as p

# GLOBALS
INPUT_DATA = "data/JWST_Cycle1_Targets.csv"
# INPUT_DATA = "test_data.dat"


def main():
    target_list = u.dict_from_tar_list(INPUT_DATA)
    target_keys = list(target_list.keys())

    # Sort for Transit Observations. Do this first, as making the
    # dictionary unique might remove transit observations and leave e.g.
    # eclipse observations of the same planet
    ind_transit = np.where(target_list["Type"] == "Transit")
    u.red_total_dict(target_list, ind_transit)

    # Make dictionary with unique entries (planets)
    u.make_dict_unique(target_list)

    # Filter out non-available entries
    u.check_nans(target_list)

    # Sort for super-Earths and mini-Neptunes
    ind_uppermass = np.where(target_list["Radius [RE]"] <= 4.)[0]
    u.red_total_dict(target_list, ind_uppermass)

    ind_lowermass = np.where(target_list["Radius [RE]"] > 0.)[0]
    u.red_total_dict(target_list, ind_lowermass)

    # Plotting
    u.rc_setup()
    p.plot_target_list(target_list)
    plt.savefig("target_list.png", dpi=300)


if __name__ == "__main__":
    main()
