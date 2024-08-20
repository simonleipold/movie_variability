### Submit script "XY.py" to HPC (Torque) cluster
import subprocess

subprocess.run(['echo "$PWD/create_is-distance_matrices.py" | qsub -l nodes=1:ppn=1,walltime=01:00:00,mem=128gb -N create_distance_matrices'], 
    shell = True)
