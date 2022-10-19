import numpy as np
import matplotlib.pyplot as plt
import util as u

# GLOBALS
INPUT_DATA = "JWST_Cycle1_Target.csv"
#INPUT_DATA = "test_data.dat"


def main():
    target_list = u.dict_from_tar_list(INPUT_DATA)
    target_keys = list(target_list.keys())
    print(f"Available keys are {target_keys}\n")

    # Make dictionary with unique entries (planets)
    u.make_dict_unique(target_list)

    # Filter out non-available entries
    u.check_nans(target_list)

    # Sort for super-Earths and mini-Neptunes
    new_indices1 = np.where(target_list["Radius [RE]"] <= 4.)[0]
    u.red_total_dict(target_list, new_indices1)
    new_indices2 = np.where(target_list["Radius [RE]"] > 0.)[0]
    u.red_total_dict(target_list, new_indices2)

    # Plotting
    u.rc_setup()
    fig, ax = plt.subplots(figsize=(12, 8))

    # Target parameters
    ax.scatter(target_list["SMA [au]"], target_list["Teff [K]"])

    for i in range(len(target_list["Target Name"])):
        ax.annotate(target_list["Target Name"][i], (target_list["SMA [au]"][i], target_list["Teff [K]"][i]))

    temp = np.linspace(2600, 7200, 5000)
    hz_bounds = u.plotable_hz_bounds(temp = temp)
    ax.fill_betweenx(temp, x1=hz_bounds["oi"], x2=hz_bounds["oo"], color="tab:green", label="OHz (Kopparapu et al. 2013)")
    ax.fill_betweenx(temp, x1=hz_bounds["ci"], x2=hz_bounds["co"], color="tab:orange", label="CHz (Kopparapu et al. 2013)")

    ax.set(xscale="log", xlabel="a [au]", ylabel="T$_{eff}$ (Host) [K]")

    plt.legend()
    plt.tight_layout()
    plt.savefig("target_list.png", dpi=300)

if __name__ == "__main__":
    main()