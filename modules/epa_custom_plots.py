import matplotlib.pyplot as plt
import pandas as pd


def plrad_steff(target_list: pd.DataFrame, savename: str) -> None:
    """Specific plot of sma-teff-rp"""
    fig, ax = plt.subplots()

    #
    target_list = target_list.drop_duplicates(["Target Name"])

    # Split targets
    subnept = target_list.loc[target_list["pl_rade"] <= 4.]
    supernep = target_list.loc[target_list["pl_rade"] > 4.]

    """
    # TEST
    subnept_c1 = subnept.loc[
        subnept["ObsCycle"] == "Cycle 1"
    ]

    subnept_c2epafree = subnept.loc[
        subnept["ObsCycle"] == "Cycle 2"
    ]
    subnept_c2epafree = subnept_c2epafree.loc[
        subnept_c2epafree["EAP [mon]"] == 0
    ]
    subnept = pd.concat(
        [subnept_c1, subnept_c2epafree], ignore_index=True
    ).drop_duplicates(["Target Name"])
    print(subnept)
    """
    print(subnept)


    # Plot gas giants in the back-ground
    ax.scatter(
        supernep["pl_orbsmax"], supernep["st_teff"],
        c="grey", alpha=0.5
    )

    # Setup for colourmap
    cmap = plt.cm.get_cmap('RdYlBu').reversed()

    # Plot targets as scatter plot
    cm = ax.scatter(
        subnept["pl_orbsmax"], subnept["st_teff"],
        edgecolor="black", s=70,
        c=subnept["pl_rade"],
        vmin=1, vmax=4, cmap=cmap
    )

    # Plot Customisation
    ax.set(
        xlabel="SMA [au]", ylabel="T$_\\mathrm{eff}$ [K]",
        xscale="log"
    )

    # Insert the colour bar
    plt.colorbar(cm, label="R$_\\mathrm{p}$ [$R_\\mathrm{E}$]")
    plt.tight_layout()
    plt.savefig(f"plots/{savename}.svg")

    return None
