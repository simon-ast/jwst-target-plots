import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import modules.util as u


def plot_target_list(target_list):
    """Plotting routine for target dictionary"""

    fig, ax = plt.subplots(figsize=(10, 7))

    # Scalable marker size by planet radius
    marker_size = 4 * target_list["Radius [RE]"]

    # Target parameters
    ax.scatter(target_list["SMA [au]"], target_list["Teff [K]"],
               s=marker_size ** 2)

    for i in range(len(target_list["Target Name"])):
        x, y = (target_list["SMA [au]"][i], target_list["Teff [K]"][i])
        ax.annotate(i + 1, (x*0.99, y*1.025))

    temperature = np.linspace(2600, 7200, 5000)
    hz_bounds = u.plotable_hz_bounds(temp=temperature)
    # Optimistic boundaries from Kopparapu et al. 2013 (for 1Me)
    ax.fill_betweenx(temperature, x1=hz_bounds["oi"], x2=hz_bounds["oo"],
                     color="tab:green", label="OHz (Kopparapu et al. 2013)",
                     alpha=0.5)
    # Conservative boundaries from (see above)
    ax.fill_betweenx(temperature, x1=hz_bounds["ci"], x2=hz_bounds["co"],
                     color="tab:orange", label="CHz (Kopparapu et al. 2013)",
                     alpha=0.5)

    ax.set(xscale="log", xlabel="Distance [au]", ylabel="T$_{eff}$ (Host) [K]",
           title="Transit Targets in JWST Cycle 1")

    # Custom legend elements
    point_handles = [
        Line2D([0], [0], marker='o',
               color='white', markerfacecolor="black",
               label=f'{i} R$_E$', markersize=(4 * fig.dpi/72.) * i)
        for i in [1, 2]
    ]

    # Use same as above, but make the Artist invisible (ms=0)
    name_handles = [
        Line2D([0], [0], marker="o", color="white", ms=0,
               label=f'{i + 1}: {target_list["Target Name"][i]}')
        for i in range(len(target_list["Target Name"]))
    ]

    # Plot clean-up
    normal_legend = plt.legend(loc="lower right", framealpha=1)

    # Add point size chart
    plt.gca().add_artist(normal_legend)
    first_add = plt.legend(handles=point_handles, loc=(.5, .9),
                           framealpha=0)

    # Add Target Name chart
    plt.gca().add_artist(first_add)
    plt.legend(handles=name_handles, loc="upper left", ncol=2, framealpha=0)

    plt.tight_layout()

    return fig, ax
