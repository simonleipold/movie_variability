### Submit script "XY.py" to HPC (Slurm) cluster
import subprocess

### Script 1
## Configurable job parameters
job_name = "create_neural_dataframes_upper" # Name of the job
output_file = f"{job_name}.out"
error_file = f"{job_name}.err"
script_to_run = "create_neural_dataframes_from_matrices_upper.py" # Name of the script to run

## Slurm job script
slurm_job = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={output_file}
#SBATCH --error={error_file}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=8G
#SBATCH --time=02:00:00

python3 $PWD/{script_to_run}
"""

## Submit the job
subprocess.run(['sbatch'], input=slurm_job, text=True)

### Script 2
## Configurable job parameters
job_name = "create_neural_dataframes_full" # Name of the job
output_file = f"{job_name}.out"
error_file = f"{job_name}.err"
script_to_run = "create_neural_dataframes_from_matrices_full.py" # Name of the script to run

## Slurm job script
slurm_job = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={output_file}
#SBATCH --error={error_file}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=8G
#SBATCH --time=02:00:00

python3 $PWD/{script_to_run}
"""

## Submit the job
subprocess.run(['sbatch'], input=slurm_job, text=True)

