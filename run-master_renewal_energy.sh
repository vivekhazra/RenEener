#!/bin/bash
#-----------------------------------------------------------------------------------------------
#                 		     Renewable Energy 			                     	|
# 		National Centre for Medium Range Weather Forecasting  			     	|
#												|
# The purpose of this script is to produce NetCDF file for renewal/wind energy from NCUM Global	|
# model outputs. Pressure level variables are derived using Exner interpolation tool developed  |
# at NCMRWF jointly by Dr. Mansi Bhowmik, Dr. A. Jaykumar and Dr. Saji Mohandas.		|
# 												|
# Team: V Hazra, Sushant Kumar, Raghavendra Ashrit, Priya Singh					|
# 												|
# Following are the sub-scripts of this main sript:						|
# 												|
# 1. input.sh											|
# 2. y-SUBMIT-SUBMIT-RE-SURF.pbs								|
# 3. y-SUBMIT-SUBMIT-RE-U.pbs									|
# 4. y-SUBMIT-SUBMIT-RE-V.pbs									|
# 5. x-UM-VERT-INTERP-RE-SURF.py 								| 
# 6. x-UM-VERT-INTERP-RE-V.py									| 
# 7. x-UM-VERT-INTERP-RE-U.py        								|
# 8. z-ENDGAME-CDO.sh										|
# 												|
#--------------------     USAGE    -- -----------------------------------------------------------
# ./run-master_renewal_energy.sh [for current date]						|
# ./run-master_renewal_energy.sh YYYYMMDD [for any other date]					|
# 												|
#--------------------    CONTACTS     -----------------------------------------------------------
# Author : Vivekananda Hazra (vivek.hazra@nic.in)                                           	|
# Version : 28-Mar-2024                                                                       	|
#------------------------------------------------------------------------------------------------
module purge
module load pbs
module unload gcc/9.3.0
module load gcc/7.2.0
export CC=cc
export CXX=CC
export FC=ftn

currdir=`pwd`
chmod +x ${currdir}/input.sh
source ${currdir}/input.sh

if [ $# -eq 0 ]; then
    pdt=$(date +"%Y%m%d")
else
    pdt=$1
fi

required_files=(
    "x-UM-VERT-INTERP-RE-SURF.py"
    "x-UM-VERT-INTERP-RE-U.py"
    "x-UM-VERT-INTERP-RE-V.py"
    "y-SUBMIT-SUBMIT-RE-SURF.pbs"
    "y-SUBMIT-SUBMIT-RE-U.pbs"
    "y-SUBMIT-SUBMIT-RE-V.pbs"
    "z-ENDGAME-CDO.sh"
    "input.sh"
)

file_missing=false
for filecheck in "${required_files[@]}"; do
    if [ ! -f "$filecheck" ]; then
        echo -e "\n
		$filecheck is missing."
        file_missing=true
    fi
done

if [ "$file_missing" = true ]; then
	echo -e "\n
		-----------------------------------------------------------------------
					Fatal Error
		Please keep the above file(s) in your running directory for proceeding.
		-----------------------------------------------------------------------
		\n"
	exit 1
fi

YYYY=`echo $pdt| cut -c1-4`
MM=`echo $pdt| cut -c5-6`
DD=`echo $pdt| cut -c7-8`

rm log-* cdo-log.* submit-script-* vert-interp-* endgame_cdo.sh

outdir=$output_dir/$pdt
logd=$logdir/$pdt

rm -rf $outdir $logd
mkdir -p $outdir $logd

paths=("${input_dir}" "${input_dir}/${pdt}" "${input_dir}/${pdt}/${cyc}")

for path in "${paths[@]}"; do
    if [ -e "$path" ]; then
        echo "Path '$path' exists."
    else
        echo -e "\n
	Error: Path '$path' does not exist. Check the date and entries in the input.sh
	\n"
	exit 1
    fi
done

files=("umglaa_pj000" "umglaa_pj024" "umglaa_pj048" "umglaa_pj072" "umglaa_pj096" "umglaa_pj120" "umglaa_pj144" "umglaa_pj168" "umglaa_pj192" "umglaa_pj216" "umglaa_pj240")

num_days=$fcst

if ! [[ $num_days =~ ^[0-9]+$ ]]; then
    echo -e "\n
		Error: Please provide a valid number of days. 
	\n"
    exit 1
fi

if [ $num_days -gt ${#files[@]} ]; then
    echo -e "\n 
		Error: Number of days exceeds the available forecast files. 
	\n"
    exit 1
fi

timeout=900
interval=5
elapsed_time=0
all_files_exist=false

while [ $elapsed_time -lt $timeout ]; do
    all_files_exist=true

    for file in "${files[@]}"; do
        if [ ! -f "${input_dir}/${pdt}/${cyc}/${file}" ]; then
            all_files_exist=false
            break
        fi
    done

    if $all_files_exist; then
        break
    fi

    echo -e "\n
		Waiting for all files to be generated ... 
	\n"
    sleep $interval
    elapsed_time=$((elapsed_time + interval))
done

if ! $all_files_exist; then
    echo -e "\n
                --------------------------------------------------------------------
                                        ERROR
                Timeout reached. All the required files have not been generated yet.
                Wait for sometime before executing the script again.
                --------------------------------------------------------------------
        \n"
else
    selected_files=("${files[@]:0:$num_days}")

    echo -e "\n
                Forecasting for $num_days day(s): \n"

    declare -a JOB_IDS_RE_U=()
    declare -a JOB_IDS_RE_V=()
    declare -a JOB_IDS_RE_SURF=()

    echo -e "Submitting all jobs at once ... \n"
    for ((i=1; i<=fcst; i++)); do
        opsfile=${input_dir}/${pdt}/${cyc}/${selected_files[i-1]}
        ordir=${input_dir}/${pdt}/${cyc}
        sed "s|DATADIR|'$opsfile'|g;s|OUTDIR|'$outdir'|g;s|LON1|$lon1|g;s|LON2|$lon2|g;s|LAT1|$lat1|g;s|LAT2|$lat2|g;s|DVAL|$i|g;s|YMD|$pdt|g;s|CYC|$cyc|g;s|OROGDIR|${ordir}|g;s|yyyy|$YYYY|g;s|mm|$MM|g;s|ddd|$DD|g" x-UM-VERT-INTERP-RE-U.py > vert-interp-re-u${i}.py
        sed "s|DATADIR|'$opsfile'|g;s|OUTDIR|'$outdir'|g;s|LON1|$lon1|g;s|LON2|$lon2|g;s|LAT1|$lat1|g;s|LAT2|$lat2|g;s|DVAL|$i|g;s|YMD|$pdt|g;s|CYC|$cyc|g;s|OROGDIR|${ordir}|g;s|yyyy|$YYYY|g;s|mm|$MM|g;s|ddd|$DD|g" x-UM-VERT-INTERP-RE-V.py > vert-interp-re-v${i}.py
        sed "s|DATADIR|'$opsfile'|g;s|OUTDIR|'$outdir'|g;s|LON1|$lon1|g;s|LON2|$lon2|g;s|LAT1|$lat1|g;s|LAT2|$lat2|g;s|DVAL|$i|g;s|YMD|$pdt|g;s|CYC|$cyc|g;s|OROGDIR|${ordir}|g;s|yyyy|$YYYY|g;s|mm|$MM|g;s|ddd|$DD|g" x-UM-VERT-INTERP-RE-SURF.py > vert-interp-re-surf${i}.py
        sed "s/NODES/$ncpu/g;s/PDT/$pdt/g;s/CYC/$cyc/g;s/ITR/$i/g;s|LOGD|$logd|g" y-SUBMIT-SUBMIT-RE-U.pbs > submit-script-re-u${i}.pbs
        sed "s/NODES/$ncpu/g;s/PDT/$pdt/g;s/CYC/$cyc/g;s/ITR/$i/g;s|LOGD|$logd|g" y-SUBMIT-SUBMIT-RE-V.pbs > submit-script-re-v${i}.pbs
        sed "s/NODES/$ncpu/g;s/PDT/$pdt/g;s/CYC/$cyc/g;s/ITR/$i/g;s|LOGD|$logd|g" y-SUBMIT-SUBMIT-RE-SURF.pbs > submit-script-re-surf${i}.pbs

	file1="submit-script-re-u${i}.pbs"
    	JOB_ID1=$(qsub "$file1")
    	JOB_IDS_RE_U+=("$JOB_ID1")
    	echo -e "\nSubmitted job with ID for U wind [day$i]: $JOB_ID1"
	file2="submit-script-re-v${i}.pbs"
        JOB_ID2=$(qsub "$file2")
        JOB_IDS_RE_V+=("$JOB_ID2")
        echo -e "\nSubmitted job with ID for V wind [day$i]: $JOB_ID2"
	file3="submit-script-re-surf${i}.pbs"
        JOB_ID3=$(qsub "$file3")
        JOB_IDS_RE_SURF+=("$JOB_ID3")
        echo -e "\nSubmitted job with ID for Single level variables [day$i]: $JOB_ID3"
    done

    echo -e "\nWaiting for Exner interpolation to finish ..."

    for JOB_ID in "${JOB_IDS_RE_U[@]}" "${JOB_IDS_RE_V[@]}" "${JOB_IDS_RE_SURF[@]}"; do
        echo -e "\n
			Waiting for job $JOB_ID to finish ...\n"
        while qstat | grep "$JOB_ID" > /dev/null; do
            sleep 20
            echo -e "\n
			Job $JOB_ID is still running. Please wait ...\n"
        done
        echo -e "Job $JOB_ID has finished."
    done

    echo -e "\nAll jobs have finished. Proceeding with the next step ..."
fi

echo -e "\n
	Going for last step ...\n"

sed "s/YYYYMMDD/$pdt/g;s/CYC/$cyc/g;s|INPATH|$outdir|g;s|OUTPATH|$outdir|g;s|ITR|$fcst|g" z-ENDGAME-CDO.sh > endgame_cdo.sh
qsub endgame_cdo.sh
qstat | grep EndGame
        while qstat | grep EndGame | grep $USER > /dev/null; do
        sleep 2
	echo -e "\nWait ..."
done
rm submit-script-* vert-interp-* endgame_cdo.sh
echo -e "\n
\n
			 ---------------------------------------------------------------
                         |        	SUCCESS: All tasks are completed.	       |
		  	 ---------------------------------------------------------------
\n
\n"
