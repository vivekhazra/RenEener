# Introduction
The purpose of this script is to produce NetCDF file for renewal/wind energy from NCUM Global model outputs. 
Pressure level variables are derived using Exner interpolation tool developed at NCMRWF jointly by Dr. Mansi Bhowmik, Dr. A. Jaykumar and Dr. Saji Mohandas.
Team: V Hazra, Sushant Kumar, Raghavendra Ashrit, Priya Singh
Following are the sub-scripts of this main sript:
1. input.sh				
2. y-SUBMIT-SUBMIT-RE-SURF.pbs								
3. y-SUBMIT-SUBMIT-RE-U.pbs									
4. y-SUBMIT-SUBMIT-RE-V.pbs									
5. x-UM-VERT-INTERP-RE-SURF.py 							 
6. x-UM-VERT-INTERP-RE-V.py									 
7. x-UM-VERT-INTERP-RE-U.py        					
8. z-ENDGAME-CDO.sh										
 												
# --------------------     USAGE    -- -----------------------------------------------------------
./run-master_renewal_energy.sh [for current date]						
./run-master_renewal_energy.sh YYYYMMDD [for any other date]				

# --------------------    CONTACTS     -----------------------------------------------------------
Author : Vivekananda Hazra (vhazra@iitbbs.ac.in)
Version : 28-Mar-2024 
