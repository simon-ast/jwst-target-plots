import numpy as np
import modules.util as u

# GLOBALS
INPUT_DATA = "data/PotTar_Cycle2_Sudeshna.csv"
PLOT_DIR = "plots/"


def main():
    targets = u.dict_cycle2_targets(INPUT_DATA)

    print(targets.iloc[0])


if __name__ == "__main__":
    main()
