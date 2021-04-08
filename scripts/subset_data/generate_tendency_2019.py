from netCDF4 import Dataset
from glob import glob
import xarray as xr
from wrf import getvar, ALL_TIMES, extract_vars, omp_set_num_threads, omp_get_num_procs


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


wrf_dir = '/WORK/nuist_chenq_2/xin/data/history/NJ/chem/20190725/lfr_lnox_waccm25_aeroff/wrfout/'
wrf_file = sorted(glob(wrf_dir+'wrfout_d03_2019-07-25_0[4-6]*'))
savedir = './data/wrfchem/tendency/'
savename = 'tendency_o3_20190725.nc'
crop_region = [118.95, 119.10, 31.93, 31.97]

wrf_in = [Dataset(f) for f in wrf_file]  # wrfpython can't deal with mdataset

# build cache
omp_set_num_threads(omp_get_num_procs())
my_cache = extract_vars(wrf_in, ALL_TIMES,
                        ('P', 'PB', 'PH', 'PHB', 'T',
                         'o3', 'advh_o3', 'advz_o3', 'chem_o3', 'vmix_o3',
                         ))

# calcualte dt
t = get_var('xtimes')
dt = t.diff(dim='Time')*60  # unit: seconds

# calculate changes
o3 = get_var('o3')
o3dt = o3.diff(dim='Time') / dt
o3dt = o3dt.rename('o3dt')*1e6
o3dt.attrs['units'] = 'pptv/s'

# calculate tendency
advh_o3 = get_var('advh_o3').diff(dim='Time') / dt * 1e6
advz_o3 = get_var('advz_o3').diff(dim='Time') / dt * 1e6
vmix_o3 = get_var('vmix_o3').diff(dim='Time') / dt * 1e6
chem_o3 = get_var('chem_o3').diff(dim='Time') / dt * 1e6
height = get_var('z', units='km').loc[advh_o3.Time]
tvmix_o3 = vmix_o3+advz_o3

# set units attrs
advh_o3.attrs['units'] = 'pptv/s'
advz_o3.attrs['units'] = 'pptv/s'
tvmix_o3.attrs['units'] = 'pptv/s'
chem_o3.attrs['units'] = 'pptv/s'

# rename
advh_o3 = advh_o3.rename('advh')
advz_o3 = advz_o3.rename('advz')
tvmix_o3 = tvmix_o3.rename('tmix')
chem_o3 = chem_o3.rename('chem')

# combine to dataarrays to one dataset
ds = xr.merge([height, advh_o3, advz_o3, tvmix_o3, chem_o3, o3dt])

# subset to convective region and average data
ds = ds.where((ds.XLONG >= crop_region[0]) &
              (ds.XLONG <= crop_region[1]) &
              (ds.XLAT >= crop_region[2]) &
              (ds.XLAT <= crop_region[3]),  # &
              # (mdbz >= 20),
              drop=True,
              ).mean(['south_north', 'west_east'])

print(ds)
comp = dict(zlib=True, complevel=9)
encoding = {var: comp for var in ds.data_vars}
ds.load().to_netcdf(path=savedir+savename,
                    mode='w',
                    engine='netcdf4',
                    encoding=encoding)
