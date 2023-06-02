import matplotlib.pyplot as plt
import numpy as np
import modules.util as u

# PLOT GLOBALS
T_LABEL = "Transit targets"
T_MARKER = "o"


def plot_backdrop(hz_indicator: str):
    """General plot setup with HZ boundaries"""
    fig, ax = plt.subplots(figsize=(8, 4))

    temperature = np.linspace(2600, 6000, 5000)
    hz_bounds = u.plotable_hz_bounds(temp=temperature)

    if hz_indicator == "area":
        # Optimistic boundaries from Kopparapu et al. 2013 (for 1Me)
        ax.fill_betweenx(temperature, x1=hz_bounds["oi"], x2=hz_bounds["oo"],
                         color="tab:green", alpha=0.5,
                         label="OHz (Kopparapu et al. 2013)")

        # Conservative boundaries from (see above)
        ax.fill_betweenx(temperature, x1=hz_bounds["ci"], x2=hz_bounds["co"],
                         color="tab:orange", alpha=0.5,
                         label="CHz (Kopparapu et al. 2013)")

    elif hz_indicator == "dashed":
        # Optimistic bounds
        opt_col = "lightgreen"
        opt_ls = "-."
        ax.plot(hz_bounds["oi"], temperature, color=opt_col,
                ls=opt_ls, label="OHz (Kopparapu et al. 2013)")
        ax.plot(hz_bounds["oo"], temperature, color=opt_col, ls=opt_ls)

        # Conservative bounds
        con_col = "tab:green"
        con_ls = "--"
        ax.plot(hz_bounds["ci"], temperature, color=con_col,
                ls=con_ls, label="CHz (Kopparapu et al. 2013)")
        ax.plot(hz_bounds["co"], temperature, color=con_col, ls=con_ls)

    ax.set(xscale="log", xlabel="SMA [au]",
           ylabel="$T_\\mathrm{eff, Host}$ [K]", ylim=(2200, 8800),
           xlim=(5e-3, .7))

    # Plot mercury as reference
    ax.scatter(0.387, 5773, c="black", marker="P")

    return fig, ax


def plot_target_list(target_list, fig, ax):
    """
    Plot transit and eclipse targets with R_p as colormap.
    Overlapping markers when both observation types are present.
    """
    # Setup for colourmap
    cmap = plt.cm.get_cmap('RdYlBu').reversed()

    # Plot targets
    cm = ax.scatter(target_list["SMA [au]"], target_list["Teff [K]"],
                    marker=T_MARKER,
                    edgecolor="black", s=70,
                    c=np.log10(target_list["Radius [RE]"]),
                    vmin=-0.15, vmax=1.3,
                    cmap=cmap)

    plt.colorbar(cm, label="log$(R_\\mathrm{p})$ [$R_\\mathrm{E}$]")

    return fig, ax
