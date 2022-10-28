import weakref
import numpy as np

FILE_NAME = "S6_wasp39b_ap6_bg7_rp^2_Table_Save.txt"

raw_array = np.genfromtxt(FILE_NAME, skip_header=10)
wavelength = raw_array[:, 0]
rp2 = raw_array[:, 2]
rp2errup = raw_array[:, 3]
rp2errdown = raw_array[:, 4]

with open("eureka_nirspec_test.dat", "w") as file:
    for i in range(len(wavelength)):
        file.write(f"{wavelength[i]} \t {rp2[i]} \t {rp2errup[i]} \n")
