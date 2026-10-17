#!/bin/bash
#SBATCH --job-name=mos2-1-relax
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=02:00:00

# load your VASP module here, e.g.: module load VASP

srun vasp_std > vasp.log
