import sys
import numpy as np

DATA_ROOT = f"{sys.path[0]}/eureka_spectra"
FILE_NAME = "ERS1366_wasp39b"
FILE_EXT = "txt"


def main():
    """DOC!"""
    filename = f"{DATA_ROOT}/{FILE_NAME}.{FILE_EXT}"
    
    raw_array = np.genfromtxt(filename, skip_header=10)
    wavelength = raw_array[:, 0]
    rp2 = raw_array[:, 2]
    rp2errup = raw_array[:, 3]
    rp2errdown = raw_array[:, 4]

    with open(f"{FILE_NAME}_spectrum.dat", "w") as file:
        for i in range(len(wavelength)):
            file.write(f"{wavelength[i]} \t {rp2[i]} \t {rp2errup[i]} \n")


if __name__ == "__main__":
    main()

