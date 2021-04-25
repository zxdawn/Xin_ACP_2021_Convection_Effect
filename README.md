# GRL_2021

## /namelists

Namelists used in the WRF-Chem simulation.

## /notebooks

Python jupyter notebooks of plotting my paper's figures.

- Fig 01.

  (a) - (b) plot_ir_swath_traj.ipynb

  (c) - (d) ozonesondes.ipynb 

- Fig 02., and Table S01.

  (a) - (b) ozone_profile_tendency_2019.ipynb

  (c) - (d) ozone_profile_tendency_2020.ipynb

- Fig 03. [(e) - (f)], Fig 04., and Fig S07.

  s5p_wrfchem_2019.ipynb and s5p_wrfchem_2020.ipynb

  

- Fig S02.

  waccm_profiles.ipynb

- Fig S03. to S06.

  comp_wrf_radar.ipynb

## /scripts

### Plotting

- Fig S01

  plot_domain.py

- Fig 03. (a) - (d)

  plot_flash_scd.py

### Processing

#### /subset_data

Some scripts used to subset original data and generate analysis data

- subset_wrfout.sh and subset_irr.sh

  Subset wrfout* files for useful variables

- generate_mean_o3_\<yyyy\>.py

  Generate mean O3 in region and pressure level

- generate_tendency_\<yyyy\>.py

  Generate summation of tendency between 8 km and 14 km.

- combine_irr_\<yyyy\>.py

  Subset irr* files and combine into one NetCDF file.

## /data

