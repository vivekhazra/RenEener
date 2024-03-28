#!/usr/bin/env python
#-------------------------------------------------------------------------------------------------------
#       Exner interpolation developed by Dr. Mansi Bhowmik, Dr.A.Jayakumar and Dr. Saji Mohandas        |
#       Exner helps converting model level to regular level                                             |
#                                                                                                       |
#       Author: Dr. Vivekananda Hazra                                                                   |
#       National Centre for Medium Range Weather Forecasting                                            |
#       Version: March 28, 2024                                                                         |
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

print('Reading 2 meter temperature ...')
t2_cntrl = iris.load_cube(datadir, iris.AttributeConstraint(STASH='m01s03i236'))
t2_cube = t2_cntrl.extract(latConstraint & lonConstraint)

print('Reading 2 meter relative humidity ...')
rh2_cntrl = iris.load_cube(datadir, iris.AttributeConstraint(STASH='m01s03i245'))
rh2_cube = rh2_cntrl.extract(latConstraint & lonConstraint)

print('Reading precipitation ...')
rf_cntrl = iris.load_cube(datadir, iris.AttributeConstraint(STASH='m01s05i226'))
rf_cube = rf_cntrl.extract(latConstraint & lonConstraint)

print('Reading surface pressure ...')
press_cntrl = iris.load_cube(datadir, iris.AttributeConstraint(STASH='m01s00i409'))
press_cube = press_cntrl.extract(latConstraint & lonConstraint)

data_lons = orogc.coord(axis='x').points
data_lats = orogc.coord(axis='y').points
#----------------------------------------------------------------------------------------------
print('Saving variables as NetCDF files ...')
# 2 meter temperature
file_name3 = 'pre_2m_temperature_YMD_CYC_dayDVAL.nc'
file_path3 = os.path.join(output_dir, file_name3)
if os.path.exists(file_path3):
    os.remove(file_path3)

root_grp = Dataset(file_path3, 'w', format='NETCDF4')
root_grp.Description = 'NCMRWF Unified Global Model Forecast (Vn11.2)'
root_grp.Conventions = 'CF-1.6'
nxdim = len(data_lons)
nydim = len(data_lats)
tdim = len(t2_cube.coord('time').points)
root_grp.createDimension('time', tdim)
root_grp.createDimension('lon', nxdim)
root_grp.createDimension('lat', nydim)
time = root_grp.createVariable('time', 'f8', ('time',))
time.units = "days since " + str(YEAR) + "-" + str(MON) + "-" + str(DAY) + " 0:0:0"
time.standard_name = "time"
time.long_name = "Same as reference time"
time.calendar = "Standard"

lon = root_grp.createVariable('lon', 'f4', ('lon',))
lon.standard_name = "longitude"
lon.long_name = "longitude"
lon.units = "degrees_east"

lat = root_grp.createVariable('lat', 'f4', ('lat',))
lat.standard_name = "latitude"
lat.long_name = "latitude"
lat.units = "degrees_north"

temp = root_grp.createVariable('t2m', 'f8', ('time', 'lat', 'lon',))
temp.long_name = "2 meter air temperature"
temp.units = "K"
temp.level = "A1"
lon[:] = t2_cube.coord(axis='x').points
lat[:] = t2_cube.coord(axis='y').points
dates = [datetime(int(YEAR),int(MON),int(DAY))+(n)*timedelta(minutes=15) for n in range(temp.shape[0])]
time[:] = date2num(dates,units=time.units,calendar=time.calendar)+0
dates = num2date(time[:],units=time.units,calendar=time.calendar)

temp[:, :, :] = t2_cube.data
root_grp.close()
print('Done saving 2m Temp')
#----------------------------------------------------------------------------------------------
# 2 meter relative humidity
file_name4 = 'pre_2m_relative_humidity_YMD_CYC_dayDVAL.nc'
file_path4 = os.path.join(output_dir, file_name4)
if os.path.exists(file_path4):
    os.remove(file_path4)

root_grp = Dataset(file_path4, 'w', format='NETCDF4')
root_grp.Description = 'NCMRWF Unified Global Model Forecast (Vn11.2)'
root_grp.Conventions = 'CF-1.6'
nxdim = len(data_lons)
nydim = len(data_lats)
tdim = len(rh2_cube.coord('time').points)
root_grp.createDimension('time', tdim)
root_grp.createDimension('lon', nxdim)
root_grp.createDimension('lat', nydim)
time = root_grp.createVariable('time', 'f8', ('time',))
time.units = "days since " + str(YEAR) + "-" + str(MON) + "-" + str(DAY) + " 0:0:0"
time.standard_name = "time"
time.long_name = "Same as reference time"
time.calendar = "Standard"

lon = root_grp.createVariable('lon', 'f4', ('lon',))
lon.standard_name = "longitude"
lon.long_name = "longitude"
lon.units = "degrees_east"

lat = root_grp.createVariable('lat', 'f4', ('lat',))
lat.standard_name = "latitude"
lat.long_name = "latitude"
lat.units = "degrees_north"

temp = root_grp.createVariable('rh2m', 'f8', ('time', 'lat', 'lon',))
temp.long_name = "2 meter relative humidity"
temp.units = "%"
temp.level = "A1"
lon[:] = rh2_cube.coord(axis='x').points
lat[:] = rh2_cube.coord(axis='y').points
dates = [datetime(int(YEAR),int(MON),int(DAY))+(n)*timedelta(minutes=15) for n in range(temp.shape[0])]
time[:] = date2num(dates,units=time.units,calendar=time.calendar)+0
dates = num2date(time[:],units=time.units,calendar=time.calendar)

temp[:, :, :] = rh2_cube.data
root_grp.close()
print('Done saving 2m RH')
#----------------------------------------------------------------------------------------------
# Precipitation
file_name5 = 'pre_total_rainfall_YMD_CYC_dayDVAL.nc'
file_path5 = os.path.join(output_dir, file_name5)
if os.path.exists(file_path5):
    os.remove(file_path5)

root_grp = Dataset(file_path5, 'w', format='NETCDF4')
root_grp.Description = 'NCMRWF Unified Global Model Forecast (Vn11.2)'
root_grp.Conventions = 'CF-1.6'
nxdim = len(data_lons)
nydim = len(data_lats)
tdim = len(rf_cube.coord('time').points)
root_grp.createDimension('time', tdim)
root_grp.createDimension('lon', nxdim)
root_grp.createDimension('lat', nydim)
time = root_grp.createVariable('time', 'f8', ('time',))
time.units = "days since " + str(YEAR) + "-" + str(MON) + "-" + str(DAY) + " 0:0:0"
time.standard_name = "time"
time.long_name = "Same as reference time"
time.calendar = "Standard"

lon = root_grp.createVariable('lon', 'f4', ('lon',))
lon.standard_name = "longitude"
lon.long_name = "longitude"
lon.units = "degrees_east"

lat = root_grp.createVariable('lat', 'f4', ('lat',))
lat.standard_name = "latitude"
lat.long_name = "latitude"
lat.units = "degrees_north"

temp = root_grp.createVariable('rf', 'f8', ('time', 'lat', 'lon',))
temp.long_name = "Total precipitation amount"
temp.units = "kg/m2"
temp.level = "A1"
lon[:] = rf_cube.coord(axis='x').points
lat[:] = rf_cube.coord(axis='y').points

dates = [datetime(int(YEAR),int(MON),int(DAY))+(n)*timedelta(minutes=15) for n in range(temp.shape[0])]
time[:] = date2num(dates,units=time.units,calendar=time.calendar)+0
dates = num2date(time[:],units=time.units,calendar=time.calendar)

temp[:, :, :] = rf_cube.data
root_grp.close()
print('Done saving Precipitation')
#----------------------------------------------------------------------------------------------
# Surface pressure
file_name6 = 'pre_surface_pressure_YMD_CYC_dayDVAL.nc'
file_path6 = os.path.join(output_dir, file_name6)
if os.path.exists(file_path6):
    os.remove(file_path6)

root_grp = Dataset(file_path6, 'w', format='NETCDF4')
root_grp.Description = 'NCMRWF Unified Global Model Forecast (Vn11.2)'
root_grp.Conventions = 'CF-1.6'
nxdim = len(data_lons)
nydim = len(data_lats)
tdim = len(press_cube.coord('time').points)
root_grp.createDimension('time', tdim)
root_grp.createDimension('lon', nxdim)
root_grp.createDimension('lat', nydim)

time = root_grp.createVariable('time', 'f8', ('time',))
time.units = "days since " + str(YEAR) + "-" + str(MON) + "-" + str(DAY) + " 0:0:0"
time.standard_name = "time"
time.long_name = "Same as reference time"
time.calendar = "Standard"

lon = root_grp.createVariable('lon', 'f4', ('lon',))
lon.standard_name = "longitude"
lon.long_name = "longitude"
lon.units = "degrees_east"

lat = root_grp.createVariable('lat', 'f4', ('lat',))
lat.standard_name = "latitude"
lat.long_name = "latitude"
lat.units = "degrees_north"

temp = root_grp.createVariable('press', 'f8', ('time', 'lat', 'lon',))
temp.long_name = "Surface air pressure"
temp.units = "Pa"
temp.level = "A1"

lon[:] = press_cube.coord(axis='x').points
lat[:] = press_cube.coord(axis='y').points

dates = [datetime(int(YEAR),int(MON),int(DAY))+(n)*timedelta(minutes=15) for n in range(temp.shape[0])]
time[:] = date2num(dates,units=time.units,calendar=time.calendar)+0
dates = num2date(time[:],units=time.units,calendar=time.calendar)

temp[:, :, :] = press_cube.data
root_grp.close()
print('Done saving Surface Pressure')
#----------------------------------------------------------------------------------------------
print("Processing completed !")
