import os
import subprocess

prefix = """#!/bin/bash
#SBATCH -J bert              # Job name
#SBATCH -o debug/mybert.%j.out     # Name of stdout output file
#SBATCH -e debug/mybert.%j.err     # Name of stderr error file
#SBATCH -p gpu-a100                  # Queue (partition) name
#SBATCH -N 1                     # Total # of nodes (must be 1 for serial)
#SBATCH -n 1                     # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 02:00:00              # Run time (hh:mm:ss)
#SBATCH --mail-user=kchen346@wisc.edu
#SBATCH --mail-type=all          # Send email at begin and end of job
"""

suffix = """
node=$SLURM_JOB_NODELIST
module load tacc-apptainer
module load cuda
echo "Node Number: ${node}"
./bert-singularity.sh
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
visited_nodes = [
]

for node in node_names:
    if node in visited_nodes:
        continue
    specify_node = f'#SBATCH -w {node}'
    script = prefix + specify_node + suffix
    script_path = f'slurm-{node}-run-bert-multi.slurm'
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

# 'c302-001', 'c302-002', 'c302-003', 'c302-004', 'c303-001', 'c303-002', 'c303-003', 'c303-004', 
# 'c304-001', 'c305-001', 'c305-002', 'c305-003', 'c305-004', 'c306-001', 'c306-002', 'c306-003', 
# 'c306-004', 'c308-001', 'c308-002', 'c308-003', 'c308-004', 'c309-001', 'c309-002', 'c309-003', 
# 'c309-004', 'c310-001', 'c310-002', 'c310-003', 'c310-004', 'c315-001', 'c315-003', 'c315-004', 
# 'c315-005', 'c315-006', 'c315-007', 'c315-008', 'c315-009', 'c315-010', 'c315-011', 'c315-012', 
# 'c315-013', 'c315-014', 'c315-015', 'c315-016', 'c316-001', 'c316-002', 'c316-003', 'c316-007', 
# 'c316-008', 'c316-009', 'c316-010', 'c316-011', 'c316-012', 'c316-013', 'c316-014', 'c316-015', 
# 'c316-016', 'c317-001', 'c317-002', 'c317-003', 'c317-004', 'c317-005', 'c317-006', 'c317-007', 
# 'c317-008', 'c317-009', 'c317-010', 'c317-011', 'c317-012'
