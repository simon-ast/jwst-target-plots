import numpy as np
import matplotlib.pyplot as plt
import util as u

# GLOBALS
INPUT_DATA = "data/JWST_Cycle1_Target.csv"
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

    # Print out valid target names
    print(target_list["Target Name"])
    print(target_list["EAP [mon]"])

    # Plotting
    u.rc_setup()
    fig, ax = plt.subplots(figsize=(12, 8))

    # Target parameters
    ax.scatter(target_list["SMA [au]"], target_list["Teff [K]"])

    for i in range(len(target_list["Target Name"])):
        x, y = (target_list["SMA [au]"][i], target_list["Teff [K]"][i])
        ax.annotate(target_list["Target Name"][i], (x, y))

    temperature = np.linspace(2600, 7200, 5000)
    hz_bounds = u.plotable_hz_bounds(temp=temperature)
    # Optimistic boundaries from Kopparapu et al. 2013 (for 1Me)
    ax.fill_betweenx(temperature, x1=hz_bounds["oi"], x2=hz_bounds["oo"],
                     color="tab:green", label="OHz (Kopparapu et al. 2013)")
    # Conservative boundaries from (see above)
    ax.fill_betweenx(temperature, x1=hz_bounds["ci"], x2=hz_bounds["co"],
                     color="tab:orange", label="CHz (Kopparapu et al. 2013)")

    ax.set(xscale="log", xlabel="a [au]", ylabel="T$_{eff}$ (Host) [K]")

    # Plot clean-up
    plt.legend()
    plt.tight_layout()
    plt.savefig("target_list.png", dpi=300)


if __name__ == "__main__":
    main()
