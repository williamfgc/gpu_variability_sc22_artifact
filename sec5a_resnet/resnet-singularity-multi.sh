#!/bin/bash
  
uarch=$(uname -m)

if [[ "$uarch" == *ppc64le* ]]; then
    echo "Base image (nvcr.io/nvidia/pytorch) only supports LINUX/AMD64 and LINUX/ARM64 architectures. Aborting." 
else
    echo "Pulling PyTorch NVIDIA image from Docker registry"
   # singularity pull docker://nvcr.io/nvidia/pytorch:22.06-py3
   # singularity run --nv docker://nvcr.io/nvidia/pytorch:22.06-py3 ./dataloader.sh
    echo "Loading dataset and running ResNet within container"
    echo "Profiling ResNet training"
    for j in {0..4}; do
        singularity run --nv docker://nvcr.io/nvidia/pytorch:22.06-py3 ./run-resnet-multi.sh $j 1 45
    done
    echo "ResNet run completed."
fi
