import matplotlib
import numpy as np
import pandas as pd
from glob import glob
import proplot as plot
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from satpy.scene import Scene
import matplotlib.patches as mpatches
from shapely.geometry.polygon import Polygon

from xin_cartopy import load_province


# set data
s5p_dir = '../data/tropomi/'
flash_dir = '../data/lightning/subset/'

f_s5p_1 = s5p_dir + 'S5P_TEST_L2__NO2____20190725*'
f_s5p_2 = s5p_dir + 'S5P_TEST_L2__NO2____20200901*'

f_ltng_1 = flash_dir + 'LtgFlashPortions20190725.csv'
f_ltng_2 = flash_dir + 'LtgFlashPortions20200901.csv'

# set tropomi passing time (output from plot_ir_swath_traj.py)
pass_t1 = pd.to_datetime('2019-07-25 05:20')
pass_t2 = pd.to_datetime('2020-09-01 05:46')
begin_t = -180  # minutes before the TROPOMI passes
end_t = 0  # minutes after the TROPOMI passes

# set plot region
extend = [118, 119.6, 31.2, 32.8]
lon_d = 0.5; lat_d = 0.5 

save_format = '.png'

def load_s5p(f_s5p):
    '''load s5p data'''
    scn = Scene(glob(f_s5p), reader='tropomi_l2')

    vnames = ['assembled_lat_bounds', 'assembled_lon_bounds',
              'nitrogendioxide_slant_column_density',
              'cloud_radiance_fraction_nitrogendioxide_window',
              'cloud_pressure_crb',
              'no2_scd_flag']

    scn.load(vnames)
    lat_bnd = scn[vnames[0]]
    lon_bnd = scn[vnames[1]]

    flag = scn[vnames[5]]
    valid = flag==0
    crf = scn[vnames[3]].where(valid)
    cp = scn[vnames[4]].where(valid)/1e2

#     error_flag = np.array([1, 4])
#     scd = scn[vnames[2]].where(~flag.isin(error_flag))
    scd = scn[vnames[2]].where(valid).where(~crf.isnull())
    scd *= 6.02214e3
    scd.attrs['units'] = '10$^{16}$ molec. / cm$^2$'
    cp.attrs['units'] = 'hPa'

    return lat_bnd, lon_bnd, scd, crf, cp, flag

def plot_data(lon_bnd, lat_bnd,
              scd, crf, cp,
              ltng, ax1, ax2, clb=False):
    # plot scd
    cmap = plot.Colormap('YlGnBu_r', 'YlOrRd',
                         ratios=(1, 1))
    

    m1 = ax1.pcolormesh(lon_bnd, lat_bnd, scd,
                        levels=256,
                        vmin=0,
                        vmax=2,
                        cmap=cmap,
                        )

    m2 = ax1.pcolormesh(lon_bnd, lat_bnd, cp,
                        levels=256,
                        vmin=100,
                        vmax=1100,
                        cmap='Blues_r',
                        cmap_kw={'right': 0.9},
                        #cmap_kw={'left': 0.2, 'right': 0.8},
                        fc='none',
                        edgecolors='face',
                        #alpha=0.5,
                        lw=0.2,
                        )



    # plot crf
#     m3 = ax2.pcolormesh(lon_bnd, lat_bnd, crf,
#                         levels=10,
#                         cmap='Greys_r',
#                         #cmap='Greys',
#                         cmap_kw={'left': 0.1, 'right': 0.9}
#                         )

    crf_bounds = np.array([0, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.97, 0.98, 0.99, 1.0])
    norm = matplotlib.colors.BoundaryNorm(boundaries=crf_bounds, ncolors=256)
    cmap_kw = {'left': 0.1}
    m3 = ax2.pcolormesh(lon_bnd, lat_bnd, crf, cmap='Ice_r', norm=norm, cmap_kw=cmap_kw)
#     m3 = ax2.pcolormesh(lon_bnd, lat_bnd, crf, cmap=cmap, norm=norm, cmap_kw=cmap_kw)

    ltng_bounds = np.concatenate([np.linspace(begin_t, -30, 6), np.linspace(-20, -0, 3)])
    norm = matplotlib.colors.BoundaryNorm(boundaries=ltng_bounds, ncolors=256)
#     cmap = plot.Colormap('RdYlGn', alpha=(0.7, 0.7))

    m4 = ax2.scatter(ltng['longitude'], ltng['latitude'],
                     c=ltng['delta'],
#                      cmap='plasma',
                     cmap='RdYlGn',
#                      cmap_kw={'shift': 180},
                     cmap_kw={'left':0.1, 'cut': 0.3, 'shift': 180},
#                      cmap='oranges_r',
#                      cmap='plasma',
#                      cmap_kw={'left': 0.3},
                     norm=norm,
#                      levels=len(ltng_bounds),
                     s=1)
    
    m4.set_facecolor("none")

    if clb:
        shrink = 1 #0.8
        ax1.colorbar(m2, loc='r',
                     ticks=plot.arange(100, 1100, 200),
                     label='Cloud Top Pressure (' + cp.attrs['units'] + ')',
                     shrink=shrink)
        ax1.colorbar(m1, loc='r',
                     ticks=plot.arange(0, 2, 0.25),
                     label='SCD$_{tropNO_2}$ (' + scd.attrs['units'] + ')',
                     shrink=shrink)
        ax2.colorbar(m3, loc='r', ticks=crf_bounds,
                     label='f$_{effNO_2}$',
                     shrink=shrink,
                     spacing="proportional")
        ax2.colorbar(m4, loc='r',
                     ticks=ltng_bounds,
#                      ticks=plot.arange(begin_t, end_t, 30),
                     label='Flash Time (mins)', shrink=shrink)

def add_patch(lat_corners, lon_corners, ax):
    poly_corners = np.zeros((len(lat_corners), 2), np.float64)
    poly_corners[:,0] = lon_corners
    poly_corners[:,1] = lat_corners
    
    poly = mpatches.Polygon(poly_corners, closed=True, ec='red4',
                            fill=False, lw=1, transform=ccrs.PlateCarree())
    ax.add_patch(poly)

# read data
lat_bnd, lon_bnd, scd, crf, cp, flag = load_s5p(f_s5p_1)
ltng = pd.read_csv(f_ltng_1)
delta = pd.to_datetime(ltng['timestamp']) - pass_t1
ltng['delta'] = delta.dt.total_seconds()/60
subset = (begin_t < ltng['delta'])& (ltng['delta'] < end_t)
ltng = ltng[subset]

f, axs = plot.subplots(proj='pcarree', nrows=2, ncols=2)
provinces = load_province()
axs.add_feature(provinces, edgecolor='k', linewidth=.3)

plot_data(lon_bnd, lat_bnd, scd, crf, cp, ltng, axs[0], axs[2])

# duplicate for another case
lat_bnd, lon_bnd, scd, crf, cp, flag = load_s5p(f_s5p_2)
ltng = pd.read_csv(f_ltng_2)
delta = pd.to_datetime(ltng['timestamp']) - pass_t2
ltng['delta'] = delta.dt.total_seconds()/60
subset = (begin_t < ltng['delta'])& (ltng['delta'] < end_t)
ltng = ltng[subset]

plot_data(lon_bnd, lat_bnd, scd, crf, cp, ltng, axs[1], axs[3], clb=True)

# # plot the high flash area
# # case 1
# lat_corners = np.array([31.866, 31.915, 32.102, 32.054])
# lon_corners = np.array([118.771, 119.093, 119.043, 118.721])
# add_patch(lat_corners, lon_corners, axs[0])
# add_patch(lat_corners, lon_corners, axs[2])

# # case 2
# lat_corners = np.array([31.852, 31.854, 32.054, 32.05])
# lon_corners = np.array([118.602, 118.927, 118.892, 118.56])
# add_patch(lat_corners, lon_corners, axs[1])
# add_patch(lat_corners, lon_corners, axs[3])



# axs[:, 0].format(latlabels=True)
# axs[1, :].format(lonlabels=True)

axs.format(
#            abc=True,
#            abcloc='l',
#            abcstyle='(a)',
           lonlabels=True,
           latlabels=True,
           collabels=[pass_t1.strftime('%Y-%m-%d %H:%M (UTC)'),
                      pass_t2.strftime('%Y-%m-%d %H:%M (UTC)')],
           dms=False,
           lonlines=lon_d,
           latlines=lat_d,
           lonlim=(extend[0], extend[1]),
           latlim=(extend[2], extend[3]),
           gridlinewidth=0.5,
           gridcolor='gray6',
           gridlabelcolor='k',
#            grid=False,
           #ticklen=5
           )

f.savefig(f'../figures/crf_ltng{save_format}')
