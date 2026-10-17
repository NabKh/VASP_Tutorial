#!/bin/bash
#SBATCH --job-name=mos2-3-hse06
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=02:00:00

# load your VASP module here, e.g.: module load VASP
cp ../2-pbe/POSCAR ../2-pbe/POTCAR ../2-pbe/WAVECAR .
srun vasp_std > vasp.log
