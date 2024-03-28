#!/bin/bash
#PBS -N EndGame
#PBS -l select=1:ncpus=36:vntype=cray_compute -l place=scatter -q NCMRWF1
#PBS -l walltime=00:05:00
#PBS -o log-cdo.output
#PBS -e log-cdo.error
#PBS -V
set -x
module load gnu/cdo/1.9.8_utility
echo "PBS_JOBID - $PBS_JOBID"

cd $CURRDIR

itr=ITR

variables=("2m_relative_humidity" "2m_temperature" "total_rainfall" "surface_pressure" "u_wind" "v_wind")

date="YYYYMMDD_CYC"

set_days() {
    if [ "$itr" -eq 4 ]; then
        days=("day1" "day2" "day3" "day4")
    elif [ "$itr" -eq 3 ]; then
        days=("day1" "day2" "day3")
    elif [ "$itr" -eq 2 ]; then
        days=("day1" "day2")
    elif [ "$itr" -eq 1 ]; then
        days=("day1")
    fi
}

for var in "${variables[@]}"; do
	val=$itr
	if [ "$val" -gt 1 ]; then
        	set_days "$val"
        	input_files=""
        	for day in "${days[@]}"; do
			input_files+="INPATH/pre_${var}_${date}_${day}.nc "
        	done
		output_file="OUTPATH/${var}_${date}.nc"
		cdo mergetime $input_files $output_file
    	else
		input_files="INPATH/pre_${var}_${date}_day1.nc"
		output_file="OUTPATH/${var}_${date}.nc"
		mv $input_files $output_file
    	fi
done

rm INPATH/pre_*.nc
