import matplotlib.pyplot as plt
import numpy as np
import modules.util as u

# PLOT GLOBALS
T_LABEL = "Transit targets"
T_MARKER = "s"
T_COLOUR = "dimgrey"
E_LABEL = "Eclipse targets"
E_MARKER = "^"
E_COLOUR = "coral"


def plot_backdrop():
    """General plot setup with HZ boundaries"""
    fig, ax = plt.subplots(figsize=(10, 5.8))

    temperature = np.linspace(2600, 6000, 5000)
    hz_bounds = u.plotable_hz_bounds(temp=temperature)

    # Optimistic boundaries from Kopparapu et al. 2013 (for 1Me)
    ax.fill_betweenx(temperature, x1=hz_bounds["oi"], x2=hz_bounds["oo"],
                     color="tab:green", label="OHz (Kopparapu et al. 2013)",
                     alpha=0.5)

    # Conservative boundaries from (see above)
    ax.fill_betweenx(temperature, x1=hz_bounds["ci"], x2=hz_bounds["co"],
                     color="tab:orange", label="CHz (Kopparapu et al. 2013)",
                     alpha=0.5)

    ax.set(xscale="log", xlabel="SMA [au]",
           ylabel="$T_\\mathrm{eff, Host}$ [K]",
           xlim=(5e-3, .7))

    return fig, ax


def plot_target_list(target_list, fig, ax):
    """DOCSTRING"""
    # Setup for colourmap
    cmap = plt.cm.get_cmap('RdYlBu').reversed()

    # Plot transit targets first
    transit = target_list.loc[target_list["Transit"] == 1.]
    cm = ax.scatter(transit["SMA [au]"], transit["Teff [K]"],
                    marker=T_MARKER, label=T_LABEL,
                    edgecolor="black",
                    c=transit["T_eq [K]"], vmin=100, vmax=2000, cmap=cmap)

    eclipse = target_list.loc[target_list["Eclipse"] == 1.]
    cm2 = ax.scatter(eclipse["SMA [au]"], eclipse["Teff [K]"],
                     marker=E_MARKER, label=E_LABEL,
                     edgecolor="black",
                     c=eclipse["T_eq [K]"], vmin=100, vmax=2000, cmap=cmap)

    plt.colorbar(cm, label="$T_\\mathrm{eq}$ [K]")

    return fig, ax
