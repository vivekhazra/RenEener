#!/bin/bash
#--------------------------------------------------------
#		  Renewal Energy			|
# 	    Author: Vivekananda Hazra			|
#  National Centre for Medium Range Weather Forecasting	|
#							|
# 	This is input file for the main script		|
#   DO NOT CHANGE BELOW UNLESS EXTREMELY NECESSARY	|
#--------------------------------------------------------
input_dir=/home/umfcst/NCUM_output/fcst
output_dir=/scratch/vhazra/WIND-ENERGY/data
logdir=/scratch/vhazra/WIND-ENERGY/logfiles
#----------------- Analysis cycle  ----------------------
cyc=00 # 00 or 12
#--------------- Forecast duration  ---------------------
fcst=4 # days. Maximum upto 4
#----------------- Indian region  -----------------------
lon1=68.0
lon2=98.0
lat1=7.0
lat2=37.0
#--------------------- nodes  ---------------------------
ncpu=1 # Strictly follow 1
