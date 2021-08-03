# Xin_ACP_2021_Convection_Effect

This repository provides the scripts and some of the data used in the 'Influence of convection on the upper tropospheric O3 and NOx budget in southeastern China' paper submitted to ACP journal.

## /namelists

Namelists used in the WRF-Chem simulation.

## /notebooks

Python jupyter notebooks of plotting my paper's figures.

- Fig 01.

  (a) - (b) plot_ir_swath_traj.ipynb

  (c) - (d) ozonesondes.ipynb 

- Fig 04., and Table 01.

  (a) - (c) ozone_profile_tendency_2019.ipynb

  (d) - (f) ozone_profile_tendency_2020.ipynb

- Fig 05. [(e) - (f)], Fig 06., and Fig S05.

  s5p_wrfchem_2019.ipynb and s5p_wrfchem_2020.ipynb

  

- Fig S02.

  waccm_profiles.ipynb

- Fig S03. and S04.

  comp_wrf_radar.ipynb

## /scripts

### Plotting

- Fig S01

  plot_domain.py

- Fig 05. (a) - (d)

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

Input data are all saved in the zenodo Dataset called [Xin_ACP_2021_Convection_Effect_data](https://doi.org/10.5281/zenodo.5154798).

Users can download the compressed file, extract it in the root directory, and rename to `data`. Then, all the Jupyter Notebooks should work well.
