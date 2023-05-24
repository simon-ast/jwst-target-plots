"""
PSEUDOCODE:
- Read (at least) names from csv
- Read ExoArchive full data frame
"""

import pandas as pd
import pyvo as vo
import numpy as np
from astroquery.simbad import Simbad


# GLOBALS
DATA_DIR = "data"


def main():
    service = vo.dal.TAPService(
        "https://exoplanetarchive.ipac.caltech.edu/TAP"
    )
#    resultset = service.search(
#        "SELECT * FROM ps "
    #    "WHERE sy_pnum > 4 "
    #    "AND default_flag = 1"
#    )
#    print(resultset)

    # Read csv-sheet
    test = pd.read_csv(f"{DATA_DIR}/JWST_cycle1_targets_RAW.csv")
    csv_names = test["Target Name"]
    print(f"Total number of csv-targets = {test.shape[0]}")
    #result_table = Simbad.query_objects(test["Target Name"])
    #print(result_table.columns)

    #exit()
    exoarch = pd.read_csv(f"{DATA_DIR}/PS_2023.04.05_05.59.00.csv",
                          comment="#")
    arch_names = exoarch["pl_name"]

    inters = np.intersect1d(csv_names, arch_names)
    print(len(inters))

if __name__ == "__main__":
    main()
