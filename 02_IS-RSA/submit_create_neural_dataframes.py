### Submit script "XY.py" to HPC (Torque) cluster
import subprocess

subprocess.run(['echo "$PWD/create_neural_dataframes_from_matrices_upper.py" | qsub -l nodes=1:ppn=1,walltime=01:00:00,mem=128gb -N create_neural_dataframes_upper'], 
    shell = True)

subprocess.run(['echo "$PWD/create_neural_dataframes_from_matrices_full.py" | qsub -l nodes=1:ppn=1,walltime=01:00:00,mem=128gb -N create_neural_dataframes_full'], 
    shell = True)
