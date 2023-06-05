# JWST Target Visualisation
Small routines to plot target parameters of JWST observational cycles.

- `target_parameters.py`: Plots parameters of JWST planetary targets for 
Transmission and Emission spectroscopy (based on the lists I have created). 
Queries the  NASA Exoplanet Archive DB to get most up-to-date parameters.

- `target_schedule.py`: Plots the expected individual observations 
(potentially filtered by e.g. planetary radius).

Exemplary output: 
- SMA distance (AU) against host star effective temperature
- Marker colour-mapped by planetary radius

![Cycle 1 Targets](plots/targets_all.svg)

Exemplary output for Cycle 1 schedule: Individual observations of transit
targets (current date marked by vertical dashed line)

![Cycle 1 Schedule](plots/schedule_cycle1_transit.svg)
