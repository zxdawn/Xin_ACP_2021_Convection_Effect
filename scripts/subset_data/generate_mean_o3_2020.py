import glob
import xarray as xr
from netCDF4 import Dataset
import pandas as pd
from wrf import getvar, ALL_TIMES, extract_vars, omp_set_num_threads, omp_get_num_procs, interplevel, ll_to_xy


wrf_path = '/WORK/nuist_chenq_2/xin/data/history/NJ/chem/20200901/lfr_500lnox/wrfout/'
wrf_file = [wrf_path+'wrfout_d04_2020-09-01_05:40:00']
savename = 'wrfout_d04_2020-09-01_05:40:00_region_500lnox'

# wrf_file = sorted(glob.glob(wrf_path+'wrfout_d04_2020-08-31_22:00:00*'))
# savename = '20200901_init'

sonde_path = '/WORK/nuist_chenq_2/xin/github/pyXZ/XZ_sonde/data/ozonesonde/'
sonde_file = '20200901_054434.csv'
crop_region = [118.85, 119, 31.87, 31.97]


def npbytes_to_str(var):
    return (bytes(var).decode("utf-8"))


def get_var(varname, units=None):
    '''Get variables from wrf file'''
    try:
        var = getvar(wrf_in, varname, timeidx=ALL_TIMES,
                     method='cat', units=units, cache=my_cache)
    except:
        # in case the var doesn't have "units" arg
        var = getvar(wrf_in, varname, timeidx=ALL_TIMES,
                     method='cat', cache=my_cache)

    return var


# get the file list
wrf_in = [Dataset(f) for f in wrf_file]  # wrfpython can't deal with mdataset

# build cache
omp_set_num_threads(omp_get_num_procs())
print('start extract')
my_cache = extract_vars(wrf_in, ALL_TIMES,
                        ('P', 'PSFC', 'PB', 'PH', 'PHB',
                         # 'T', 'QVAPOR', 'QCLOUD',
                         # 'HGT', 'U', 'V', 'W',
                         'o3', 'no2', 'co',
                         ))
print('end extract')


# get variables
o3 = get_var('o3')*1e3
z = get_var('z', units='km')
xy = ll_to_xy(wrf_in[0], longitude=crop_region[:2], latitude=crop_region[2:])

sonde = pd.read_csv(sonde_path + sonde_file)

sonde_z = sonde[sonde['Dropping'] == 0]['HeightFromGps'] / 1e3

o3_interp = interplevel(o3, z, sonde_z)
o3_interp.attrs['units'] = 'ppbv'
# crop tp crop_region
o3_interp = o3_interp.sel(west_east=slice(xy[0, 0].values, xy[0, 1].values), south_north=slice(xy[1, 0].values, xy[1, 1].values))

medians = o3_interp.median(dim=['south_north', 'west_east']).rename('medians')
quantiles = o3_interp.quantile([0.05, 0.25, 0.75, 0.95], dim=['south_north', 'west_east']).rename('quantiles')
ds = xr.merge([medians, quantiles])

# set compression
comp = dict(zlib=True, complevel=9)
encoding = {var: comp for var in ds.data_vars}
ds.to_netcdf(path=savename,
             mode='w',
             engine='netcdf4',
             encoding=encoding)
