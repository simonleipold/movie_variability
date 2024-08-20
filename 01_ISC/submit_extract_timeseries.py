### Submit script "XY.py" to HPC (Torque) cluster
import subprocess

subprocess.run(['echo "$PWD/extract_timeseries.py" | qsub -l nodes=1:ppn=1,walltime=48:00:00,mem=128gb -N extract_timeseries'], 
    shell = True)
