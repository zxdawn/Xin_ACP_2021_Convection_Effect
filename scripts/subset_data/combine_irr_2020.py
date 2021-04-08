import os
import pandas as pd
import xarray as xr
import numpy as np
from glob import glob
from netCDF4 import Dataset
from wrf import getvar, ALL_TIMES, extract_vars

# set paras
bottom = 8  # km
top = 14  # km
units = 'molec'  # ppt or molec

lnox_dir = '/WORK/nuist_chenq_2/xin/data/history/NJ/chem/20200901/lfr_500lnox/'
savename = f'irr_20200901_lnox500_{bottom}-{top}km.nc'

lnox_dir = '/WORK/nuist_chenq_2/xin/data/history/NJ/chem/20200901/ltng_nolnox/'
savename = f'irr_20200901_nolnox_{bottom}-{top}km.nc'

print(f'Savename {savename}')

irr_lnox = sorted(glob(lnox_dir+'irr/subset/IRR_DIAG_d04_2020-09-01_0[4-6]*'))
wrfout_files = [f.replace('irr', 'wrfout').replace('IRR_DIAG', 'wrfout') for f in irr_lnox]
savedir = './data/wrfchem/irr/'

# all needed reactions
reactions = ['ALKO2_NO_IRR', 'C2H5O2_NO_IRR', 'C3H7O2_NO_IRR', 'CH3CO3_NO_IRR', 'CH3O2_NO_IRR', 'ENEO2_NO_IRR', 'EO2_NO_IRR', 'ISOPNO3_NO_IRR', 'ISOPO2_NO_IRR', 'MACRO2_NO_IRR', 'MACRO2_NO_a_IRR', 'MCO3_NO_IRR', 'MEKO2_NO_IRR', 'NO3_NO_IRR', 'NO_HO2_IRR', 'O3_NO_IRR', 'PO2_NO_IRR', 'RO2_NO_IRR', 'TERPO2_NO_IRR', 'TOLO2_NO_IRR', 'XO2_NO_IRR', 'C10H16_O3_IRR', 'C2H4_O3_IRR', 'C3H6_O3_IRR', 'CH3CO3_HO2_IRR', 'HO2_O3_IRR', 'ISOP_O3_IRR', 'MACR_O3_IRR', 'MCO3_HO2_IRR', 'MVK_O3_IRR', 'NO3_HV_IRR', 'O3_HV_IRR', 'O3_HV_a_IRR', 'O3_NO2_IRR', 'O3_NO_IRR', 'OH_O3_IRR', 'O_M_IRR', 'O_O3_IRR', 'O1D_CB4_H2O_IRR']

# set the region and height range
crop_region = [118.7, 118.85, 31.87, 31.97]

# open irr and wrfout data
ds_lnox = xr.open_mfdataset(irr_lnox, combine='nested', concat_dim='Time')
ds_wrfout = xr.open_dataset(wrfout_files[0])
nc_wrfout = [Dataset(f) for f in wrfout_files]

my_cache = extract_vars(nc_wrfout, ALL_TIMES, ('T'))


def mean_irr(ds_wrfout, nc_wrfout, ds_irr, reactions):
    '''Get the mean IRR in the crop_region and from bottom to top'''
    # pick interested reactions
    ds_irr = ds_irr[reactions]

    # get basic info from the wrfout file
    lon = ds_wrfout.XLONG.isel(Time=0)
    lat = ds_wrfout.XLAT.isel(Time=0)
    z = getvar(nc_wrfout, 'z', units='km', timeidx=ALL_TIMES, method='cat', cache=my_cache)
    p = getvar(nc_wrfout, 'pressure', timeidx=ALL_TIMES, method='cat', cache=my_cache)
    t = getvar(nc_wrfout, 'T', timeidx=ALL_TIMES, method='cat', cache=my_cache)

    # calculate the mean IRR in the region
    subset = (lon >= crop_region[0]) & (lon <= crop_region[1]) \
        & (lat >= crop_region[2]) & (lat <= crop_region[3]) \
        & (z >= bottom) & (z <= top)

    # we use the "difference" here as the IRRs are integrated values
    if units == 'ppb':
        ds_irr = ds_irr.where(subset.drop_vars(['Time', 'XTIME']), drop=True)\
                         .mean(dim=['south_north', 'west_east', 'bottom_top'])\
                         .diff('Time')
    elif units == 'molec':
        # molec. cm-3
        NA = 6.022e23
        R = 8.314
        ds_irr = (ds_irr * p * NA / (R*t) * 1e-10).where(subset.drop_vars(['Time', 'XTIME']), drop=True)\
            .mean(dim=['south_north', 'west_east', 'bottom_top'])\
            .diff('Time')

    return ds_irr


def conv_da(ds_irr):
    '''Convert IRR Dataset to DataArray and add coords'''
    # get the datetime for the Time coordinate
    times = pd.to_datetime(pd.Series([os.path.basename(f) for f in irr_lnox]), format='IRR_DIAG_d04_%Y-%m-%d_%H:%M:%S_subset')[1:]
    times = times.to_xarray().drop_vars('index').rename({'index': 'Time'})

    # set the time coords and rename
    da_irr = ds_irr.assign_coords({'Time': times}).to_array(dim='RXN', name='IRR').transpose()

    # convert the unit to pptv/s
    delta = times.diff(dim='Time')[0] / np.timedelta64(1, 's')  # seconds
    if units == 'ppt':
        da_irr = da_irr * 1e6 / delta.values
        da_irr.attrs['units'] = 'pptv/s'
    elif units == 'molec':
        da_irr = da_irr / delta.values
        da_irr.attrs['units'] = 'molec. cm$^{-3}$ s$^{-1}$'

    da_irr.attrs['title'] = f'Mean IRRs between {bottom} km and {top} km'
    da_irr.attrs['crop_region'] = crop_region

    return da_irr


# calculate irr
print('Start calculating mean IRRs ... ')
ds_lnox = mean_irr(ds_wrfout, nc_wrfout, ds_lnox, reactions)
da_lnox = conv_da(ds_lnox)
print('Finish calculating mean IRRs ... ')

# save to netcdf
comp = dict(zlib=True, complevel=9)
print(f'Saving to {savedir+savename} ...')
da_lnox.to_netcdf(f'{savedir+savename}', encoding={'IRR': comp}, compute=True, engine='netcdf4')
