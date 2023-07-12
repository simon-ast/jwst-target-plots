import pyvo
import numpy as np
import pandas as pd
import astropy.constants as c
import matplotlib.pyplot as plt
import modules.util as u


# TODO: Include ESM calculation
# TODO: Comparison to JWST targets


def main():
    # Query EPA for planet parameters, and calculate TSM values
    query_file = "data/target_tsm-query.txt"
    query_res = create_tsm_table(query_file)

    # Save the full results, as well as the best 20 (maybe?)
    query_res.to_csv("plots/tsm_table.csv", sep="\t", index=False)
    print(query_res.head(20).sort_values(by="sy_dist"))

    # Plot and save TSM results
    plot_tsm_table(query_res, "tsm_table")
    plot_tsm_table(query_res.head(20), "tsm_table_top20")


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
    query_res["TSM"] = kempton_tsm(query_res)

    # Restrict results to only non-NaN values for TSM, and sort
    # by descending TSM-value
    query_res = query_res.dropna(subset="TSM").sort_values(
        by="TSM", ascending=False
    )

    return query_res


def plot_tsm_table(tsm_table: pd.DataFrame, save_id: str) -> None:
    """Plot TSM values in reference to some specified parameter"""
    fig, ax = plt.subplots()

    cmap = plt.scatter(tsm_table["sy_dist"], tsm_table["TSM"],
                       c=tsm_table["pl_rade"], cmap="viridis")
    plt.colorbar(cmap, label="Planet radius [R$_\\mathrm{E}$]")

    ax.set(
        xlabel="System distance [pc]", xscale="log",
        ylabel="TSM", yscale="log"
    )

    plt.tight_layout()
    plt.savefig(f"plots/target_spectroscopy-metric/target_{save_id}.svg")
    plt.show()


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


def kempton_tsm(eqt: pd.DataFrame) -> pd.Series:
    """
    Calculate the TSM value as described in Kempton et al. (2018)
    """
    # Correct values for T_eq
    t_eq = kempton_teq(eqt)

    # Split up the calculation
    enum = (eqt["pl_rade"]) ** 3 * t_eq
    denom = (eqt["pl_masse"] * eqt["st_rad"] ** 2)
    factor = 10 ** (- eqt["sy_jmag"] / 5)

    # Scale factor assignment
    scale_factor = np.array(
        [kempton_scale_factor(radius) for radius in eqt["pl_rade"]]
    )

    # Put everything together to calculate TSM
    tsm = scale_factor * enum / denom * factor

    return tsm


def kempton_teq(eqt: pd.DataFrame) -> pd.Series:
    """
    Assignment of equilibrium temperature according to Kempton et al. (2018)
    """
    t_eq = eqt["st_teff"] * np.sqrt(
        (eqt["st_rad"] * c.R_sun) / (eqt["pl_orbsmax"] * c.au)
    ) * (1/4) ** (1/4)

    return t_eq


def kempton_scale_factor(pl_rad):
    """Assign a scale-factor to each planet following Table 1"""
    scale_factors = [0.190, 1.26, 1.28, 1.15]

    if pl_rad <= 1.5:
        return scale_factors[0]

    elif pl_rad <= 2.75:
        return scale_factors[1]

    elif pl_rad <= 4.0:
        return scale_factors[2]

    elif pl_rad <= 10.0:
        return scale_factors[3]

    else:
        return scale_factors[3]
        # This should not be able to trigger when only querying sub-Neptunes
    #    print("WHAT?")


if __name__ == "__main__":
    u.rc_setup()
    main()
