import os
import subprocess

prefix = """#!/bin/bash
#SBATCH -J resnet              # Job name
#SBATCH -o debug/myresnet.%j.out     # Name of stdout output file
#SBATCH -e debug/myresnet.%j.err     # Name of stderr error file
#SBATCH -p gpu-a100                  # Queue (partition) name
#SBATCH -N 1                     # Total # of nodes (must be 1 for serial)
#SBATCH -n 1                     # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 02:00:00              # Run time (hh:mm:ss)
#SBATCH --mail-user=crhowarth@wisc.edu
#SBATCH --mail-type=all          # Send email at begin and end of job
"""

suffix = """
node=$SLURM_JOB_NODELIST
module load tacc-apptainer
echo "Node Number: ${node}"
./resnet-singularity-multi.sh
"""


def get_slurm_node_names(partition_name):
    # Command to get node names from the specified partition
    command = ['sinfo', '-N', '-h', '-p', partition_name, '--format=%N']

    # Execute the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        print("Error executing sinfo command:", result.stderr)
        return None

    # Split the output into a list of node names
    node_names = result.stdout.strip().split('\n')

    return node_names


partition_name = 'gpu-a100'
node_names = get_slurm_node_names(partition_name)
exclude_list = []
visited_nodes = []

for node in node_names:
    if node in visited_nodes:
        continue
    specify_node = f'#SBATCH -w {node}'
    script = prefix + specify_node + suffix
    script_path = f'slurm-{node}-run-resnet-multi.slurm'
    print(script_path)
    with open(script_path, 'w') as f:
        f.write(script)
    # submit this file to the sbatch
    result = subprocess.run(['sbatch', script_path],
                            capture_output=True, text=True)

    # Check if sbatch command was successful
    if result.returncode == 0:
        print(f"Job successfully submitted for node {node}")
        visited_nodes.append(node)
    else:
        print(f"Failed to submit job for node {node}. Error: {result.stderr}")

    if os.path.exists(script_path):
        os.remove(script_path)

with open('visited.txt', 'a') as f:
    for node in visited_nodes:
        f.write("'" + node + "'" + ', ')

print("All jobs have been submitted.")

