import modules.tsm_calculations as tsm
import modules.simbad_query as sq
import matplotlib.pyplot as plt
import modules.util as u
import pandas as pd
import numpy as np
import logging
import pyvo

# TODO: Include ESM calculation
GEN_PLOTS = False
INDIV_SYSTEM = "TOI-178"


def main():
    # Set up logging solution for SIMBAD query warning
    simbad_log = "output/target_spectroscopy-metric/query.log"
    logging.basicConfig(filename=simbad_log, level=logging.INFO)
    # This captures astropy warnings
    logging.captureWarnings(True)
    print(
        f"\nBe aware that SIMBAR query errors are logged into "
        f"{simbad_log} rather than displayed"
    )

    # Name the query to be done
    id_name = "tsm_table"

    # Query EPA for planet parameters, and calculate TSM values
    query_file = "data/target_tsm-query.txt"
    query_res = create_tsm_table(query_file)

    # Make a quick probe if targets are in JWST or ARIEL lists
    sq.target_comparison(query_res)

    # Save the full results, as well as the best 20 (maybe?)
    query_res.to_csv(
        f"output/target_spectroscopy-metric/{id_name}.csv",
        sep="\t", index=False
    )

    # Print the top-TSM results to the terminal
    print_col_interest = [
        "pl_name", "pl_rade", "pl_masse", "pl_dens", "TSM", "sy_pnum",
        "sy_jmag", "td_perc", "ARIEL", "JWST", "st_teff", "pl_eqt"
    ]
    
    # Plot and save TSM results
    if GEN_PLOTS is True:
        plot_tsm_table(query_res, id_name)

    # Plot individual systems
    if INDIV_SYSTEM is not False:
        individual_system(INDIV_SYSTEM, query_res, print_col_interest)


def individual_system(
        query_name: str, query_res: pd.DataFrame, print_query: list
) -> None:
    """Generate specialised output for individual systems"""
    indiv_system = query_res.loc[query_res["hostname"] == query_name]
    print(f"\n{indiv_system[print_query]}\n")
    plot_indiv_system(query_res, query_name)


def create_tsm_table(query_file: str) -> pd.DataFrame:
    """
    Reads a specified ADQL-query and returns a data frame with system
    parameters
    """
    # Construct query from global constraints
    with open(query_file, "r") as query_file:
        adql_query = query_file.read().replace('\n', ' ')

    # Execute query and add TSM value
    query_res = query_nasa_epa(adql_query)
    query_res["TSM"] = tsm.kempton_tsm(query_res)

    # Add some additional values
    tsm.transit_estimations(query_res)

    # Restrict results to only non-NaN values for TSM, and sort
    # by descending TSM-value
    query_res = query_res.dropna(subset="TSM").sort_values(
        by="TSM", ascending=False
    )

    return query_res


def plot_tsm_table(tsm_table: pd.DataFrame, save_id: str) -> None:
    """Plot TSM values in reference to some specified parameter"""
    # 1st figure: System distance against TSM, radius colour-map
    fig, ax = plt.subplots()
    cmap = ax.scatter(tsm_table["sy_dist"], tsm_table["TSM"],
                       c=tsm_table["pl_rade"], cmap="viridis")
    plt.colorbar(cmap, label="Planet radius [R$_\\mathrm{E}$]")

    ax.set(
        xlabel="System distance [pc]", xscale="log",
        ylabel="TSM", yscale="log"
    )

    plt.tight_layout()
    plt.savefig(f"output/target_spectroscopy-metric/target_{save_id}.svg")

    # 2nd figure: orbital period against radius, TSM colour-map
    fig2, ax2 = plt.subplots()
    cmap2 = ax2.scatter(
        tsm_table["pl_orbper"], tsm_table["pl_rade"],
        c=np.log10(tsm_table["TSM"]), cmap="viridis"
    )
    plt.colorbar(cmap2, label="log$_{10}$(TSM)")
    ax2.set(
        xlabel="P [d]", xscale="log",
        ylabel="Planet radius [R$_\\mathrm{E}$]"
    )
    plt.tight_layout()
    plt.savefig(
        f"output/target_spectroscopy-metric/target_{save_id}_params.svg"
    )


def plot_indiv_system(query_res: pd.DataFrame, hostname: str) -> None:
    """Some informational plots for individual systems"""
    # Subframe for system of interest
    subframe = query_res.loc[query_res["hostname"] == hostname]
    if subframe.empty:
        print(f"CANNOT FIND {hostname}!")
        exit()

    # Figure: mass against radius, TSM colour-map
    # Figure body
    fig, ax = setup_density_plot()

    # Error in radius and mass
    rad_err = [subframe["pl_radeerr1"], subframe["pl_radeerr2"] * -1]
    mass_err = [subframe["pl_masseerr1"], subframe["pl_masseerr2"] * -1]

    # Use error bars from first, and overlay scatterplot with colour-map
    ax.errorbar(
        subframe["pl_masse"], subframe["pl_rade"], xerr=mass_err,
        yerr=rad_err, marker="none", fmt="none", c="black", zorder=2
    )

    cmap3 = ax.scatter(
        subframe["pl_masse"], subframe["pl_rade"],
        c=subframe["pl_eqt"], cmap="plasma",
        edgecolors="black", zorder=3
    )
    plt.colorbar(cmap3, label="T$_\\mathrm{eq}$ [K]", )

    # Some plotting parameters
    planet_total, x_lim, y_lim = calc_density_plot_pars(subframe)

    # Plot formatting
    ax.set(
        xlabel="M$_\\mathrm{p}$ [M$_\\mathrm{E}$]", xscale="log",
        ylabel="R$_\\mathrm{p}$ [R$_\\mathrm{E}$]",
        title=f"{hostname} ({planet_total} system members in NASA EPA)",
        xlim=x_lim, ylim=y_lim
    )
    plt.legend(title="Zeng et al. (2016)", loc="upper left")
    plt.tight_layout()

    # Save the plot
    plot_loc = "output/target_spectroscopy-metric/individual_systems"
    plt.savefig(
        f"{plot_loc}/target_{hostname}_density.svg"
    )


def setup_density_plot():
    """Set up the mass-radius plots for individual systems"""
    fig, ax = plt.subplots()

    # Iso-lines from Zheng et al. (2016)
    plot_density_contour(
        ax, "zeng2016_5percH2_rockycore_500k.dat", ":",
        "5% H$_2$ (rocky, 500 K)"
    )
    plot_density_contour(
        ax, "zeng2016_5percH2_watercore_500k.dat", "-.",
        "5% H$_2$ (water-rich, 500 K)"
    )
    plot_density_contour(
        ax, "zeng2016_100percwater.dat", "--",
        "100% H$_2$O envelope (500 K)"
    )
    plot_density_contour(
        ax, "zeng2016_notatmo_earthcore.dat", "-",
        "Rocky (no atmosphere)"
    )

    return fig, ax


def plot_density_contour(
        axis: plt.Axes, file_name: str,
        line_style: str, line_label: str
) -> None:
    """Plot iso-contours from Zheng et al. (2016) values"""
    # Read the correct file
    data_loc = "data"
    filename = f"{data_loc}/{file_name}"
    data_set = pd.read_csv(filename, sep="\t")

    axis.plot(
        data_set["mass"], data_set["radius"], zorder=0,
        ls=line_style, label=line_label, c="black", lw=2
    )

    return None


def calc_density_plot_pars(subframe: pd.DataFrame) -> tuple:
    """Calculate some plotting and labeling parameters"""
    # Total number of planets in the system for reference
    number_of_planet = subframe["sy_pnum"].to_numpy()[0]

    # Standard values for x (mass) and y (radius) boundaries
    x_limits = (0.11, 15)
    y_limits = (0.1, 4)

    # Adjust mass boundaries
    if np.min(subframe["pl_masse"]) < x_limits[0]:
        new_low = np.min(subframe["pl_masse"] + subframe["pl_masseerr2"]) * 0.9
        x_limits = (new_low, 15)

    return number_of_planet, x_limits, y_limits


def query_nasa_epa(query_string: str) -> pd.DataFrame:
    """
    Query the NASA Exoplanet Archive using TAP through pyVO. The
    values returned here are the ones flagged as "default" in the EPA
    catalogue.
    """
    # Set up NASA EPA query with pyVO
    tap_source = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    service = pyvo.dal.TAPService(tap_source)

    # Use pyVO to query NASA EPA
    result_table = service.search(query_string)

    return result_table.to_table().to_pandas()


if __name__ == "__main__":
    u.rc_setup()
    main()
