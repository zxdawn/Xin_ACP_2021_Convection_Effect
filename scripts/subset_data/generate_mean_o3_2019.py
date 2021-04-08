import glob
import xarray as xr
from netCDF4 import Dataset
import pandas as pd
from wrf import getvar, ALL_TIMES, extract_vars, omp_set_num_threads, omp_get_num_procs, interplevel

wrf_path = '/WORK/nuist_chenq_2/xin/data/history/NJ/chem/20190725/lfr_lnox_waccm25_aeroff_500lno/wrfout/'
wrf_file = [wrf_path+'wrfout_d03_2019-07-25_06:00:00']
savename = 'wrfout_d03_2019-07-25_06:00:00_region_500lnox'

# wrf_file = sorted(glob.glob(wrf_path+'wrfout_d03_2019-07-25_00:00:00*'))
# savename = '20190725_init'

sonde_path = '/WORK/nuist_chenq_2/xin/github/pyXZ/XZ_sonde/data/ozonesonde/'
sonde_file = '20190725_0634.csv'

# tseries = pd.date_range(start='2019-07-25 05:40:00',
#                        end='2019-07-25 06:40:00',
#                        freq='10min')

crop_region = [118.95, 119.10, 31.93, 31.97]


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

sonde_z = pd.read_csv(sonde_path + sonde_file)['h']/1e3  # km

o3_interp = interplevel(o3, z, sonde_z)
o3_interp.attrs['units'] = 'ppbv'


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
