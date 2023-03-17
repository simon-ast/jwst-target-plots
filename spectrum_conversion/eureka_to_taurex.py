import sys
import numpy as np
import matplotlib.pyplot as plt

DATA_ROOT = f"{sys.path[0]}/"
FILE_NAME = "wasp39b-cut-60bins"
FILE_EXT = "txt"


def main():
    """DOC!"""
    filename = f"{DATA_ROOT}/{FILE_NAME}.{FILE_EXT}"
    
    raw_array = np.genfromtxt(filename, skip_header=10)
    wavelength = raw_array[:, 0]
    rp2 = raw_array[:, 2]
    rp2err = (raw_array[:, 3] + raw_array[:, 4]) / 2
    
    with open(f"{FILE_NAME}_spectrum.dat", "w") as file:
        for i in range(len(wavelength)):
            file.write(f"{wavelength[i]} \t {rp2[i]} \t {rp2err[i]} \n")
    
    plt.scatter(wavelength, rp2)
    plt.show()


if __name__ == "__main__":
    main()

