#!/usr/bin/env python
#-------------------------------------------------------------------------------------------------------
# 	Exner interpolation developed by Dr. Mansi Bhowmik, Dr.A.Jayakumar and Dr. Saji Mohandas	|
#	Exner helps converting model level to regular level						|
#													|
#	Author: Dr. Vivekananda Hazra									|
#	National Centre for Medium Range Weather Forecasting						|
# 	Version: March 28, 2024										|
#-------------------------------------------------------------------------------------------------------
import os, sys, time, subprocess, errno
import numpy as np
import iris
from cf_units import Unit
import multiprocessing as mp
import multiprocessing.pool as mppool
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from netCDF4 import Dataset
import netCDF4 as nc
from datetime import datetime, timedelta
from netCDF4 import num2date, date2num, date2index
iris.FUTURE.netcdf_no_unlimited = True
#-----------------------------------------------------
YEAR=yyyy
MON=mm
DAY=ddd + DVAL - 1

sys.path.append('/home/umreg/smallapps/Exner_util/AGL')
from ml2hl_interp import modelLevel2RegularHeight

targetHeight = [50, 80, 100, 120, 150]
targetHeight = np.array(targetHeight)

datadir = DATADIR
output_dir = OUTDIR
orog_dir = 'OROGDIR/umgla.pp0'

lonConstraint = iris.Constraint(longitude=lambda cell: LON1 < cell < LON2)
latConstraint = iris.Constraint(latitude=lambda cell: LAT1 < cell < LAT2)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    os.chmod(output_dir, 0o755)

print('Reading Orography data ...')
orog = iris.load_cube(orog_dir, iris.AttributeConstraint(STASH='m01s00i033'))
orogc = orog.extract(latConstraint & lonConstraint)

print('Reading U component ...')
u_cntrl = iris.load_cube(datadir, iris.AttributeConstraint(STASH='m01s00i002'))
u_cntrl = u_cntrl.extract(latConstraint & lonConstraint)
u_cntrl = u_cntrl.regrid(orogc[0], iris.analysis.Linear())
u_cube = modelLevel2RegularHeight(u_cntrl, targetHeight)
data_lons = orogc.coord(axis='x').points
data_lats = orogc.coord(axis='y').points
#----------------------------------------------------------------------------------------------
print('Saving variable as a NetCDF file ...')
# U component of  wind
file_name1 = 'pre_u_wind_YMD_CYC_dayDVAL.nc'
file_path1 = os.path.join(output_dir, file_name1)
if os.path.exists(file_path1):
    os.remove(file_path1)

root_grp = Dataset(file_path1, 'w', format='NETCDF4')
root_grp.Description = 'NCMRWF Unified Global Model Forecast (Vn11.2)'
root_grp.Conventions = 'CF-1.6'
nxdim = len(data_lons)
nydim = len(data_lats)
tdim = len(u_cube.coord('time').points)
nlev = len(u_cube.coord('height').points)
root_grp.createDimension('time', tdim)
root_grp.createDimension('lev', nlev)
root_grp.createDimension('lon', nxdim)
root_grp.createDimension('lat', nydim)
time = root_grp.createVariable('time', 'f8', ('time',))
time.units = "days since " + str(YEAR) + "-" + str(MON) + "-" + str(DAY) + " 0:0:0"
time.standard_name = "time"
time.long_name = "reference time"
time.calendar = "Standard"

lev = root_grp.createVariable('lev', 'f4', ('lev',))
lev.standard_name = "height"
lev.long_name = "height"
lev.units = "m"

lon = root_grp.createVariable('lon', 'f4', ('lon',))
lon.standard_name = "longitude"
lon.long_name = "longitude"
lon.units = "degrees_east"

lat = root_grp.createVariable('lat', 'f4', ('lat',))
lat.standard_name = "latitude"
lat.long_name = "latitude"
lat.units = "degrees_north"

temp = root_grp.createVariable('u', 'f8', ('time', 'lev', 'lat', 'lon',))
temp.long_name = "Zonal wind speed"
temp.units = "m/s"
temp.level = "A1"

lon[:] = u_cube.coord(axis='x').points
lat[:] = u_cube.coord(axis='y').points
lev[:] = u_cube.coord('height').points
dates = [datetime(int(YEAR),int(MON),int(DAY))+(n)*timedelta(minutes=15) for n in range(temp.shape[0])]
time[:] = date2num(dates,units=time.units,calendar=time.calendar)+0
dates = num2date(time[:],units=time.units,calendar=time.calendar)

temp[:, :, :, :] = u_cube.data
root_grp.close()
print('Done saving U')
#----------------------------------------------------------------------------------------------
print("Processing completed !")
