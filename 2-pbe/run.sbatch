#!/bin/bash
#SBATCH --job-name=mos2-2-pbe
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=02:00:00

# load your VASP module here, e.g.: module load VASP
cp ../1-relax/CONTCAR POSCAR
cp ../1-relax/POTCAR .
srun vasp_std > vasp.log
