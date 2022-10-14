# Pseudocode

"""
Read in data from target list
    - Collect the full target list, and set e.g. mass boundaries
    - Make each target its own object (class), storing
        - Target name
        - Target mass
        - Target radius
        - Host SpT
        - Host temperature (?)

Calculate HZ with easy equation (luminosity scaling) -> 0.77 and 1.77 scaling factors (Kasting?)
    - Kopparapu et al. with conservative estimates maybe? Or optimistic
    - Kopparapu need temperature and luminosity as stellar parameters

PLOTTING:
SpT (Temp) vs. distance with marked area for HZ
"""

import numpy as np
import matplotlib.pyplot as plt

class TargetList:
    def __init__(self, raw_array) -> None:
        self.names = raw_array[:, 0]
        self.mass_me = np.array(raw_array[:, 2], dtype=float)
        self.dist_au = np.array(raw_array[:, 3], dtype=float)
        self.host_spt = raw_array[:, 4]


def hz_kasting(stellar_lum):
    solar_lum = 0
    scaled_lum = np.sqrt(stellar_lum / solar_lum)

    inner_bound = scaled_lum * 0.77
    outer_bound = scaled_lum * 1.77


TEST_DATA = "test_data.dat"
full_array = np.genfromtxt(TEST_DATA, dtype=str, delimiter="\t", skip_header=1)
print(full_array[:, :5])

cycle1_targets = TargetList(full_array)
print(cycle1_targets.mass_me)
