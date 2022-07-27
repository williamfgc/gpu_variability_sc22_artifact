# Section 5E: BERT Pretraining on NVIDIA GPUs

## Application Overview and Directory Structure
We ran the pre-training phase of BERT-Large Uncased. Note that we did not complete training on the entire training set. Our training ran across four GPUs on one node. Because we only use one node, we do not need to use any `mpi` commands. 
For running BERT, please see sections [Prerequisites](#prerequisites) and [Running BERT Pretraining on NVIDIA GPUs](#run-the-application).

Below is a breakdown of this directory. 
```
├── config: a directory containing configuration details regarding locating the dataset and other parameters
├── src: a directory containing source files used in the pytorch bert implementation
├── utils: a directory containing utility files used in the pytorch bert implementation
├── run_pretraining.py: main python file called to launch BERT
├── README.md: contains BERT Pretraining specific instructions on running the application and adjusting input configurations
```

## Adjusting Input Configurations
To adjust configuration parameters, update `scripts/run_pretraining_lamb.sh`. Will also need to update config/bert_pretraining_phase1_config.json so the vocab file points correctly to your given data file. (Rest from resnet) Specifically, update `NGPUS` and `NNODES` to adjust the number of gpus and/or nodes, respectively. Update line 19 to adjust the batch size. The default number of gpus is 4, number of nodes is 1, and batch size is 64.

## Prerequisites
* Machine with an NVIDIA GPU
* Relevant GPU drivers installed
* Compilation and launch scripts assume one or more Volta Class GPU (arch_70, compute_70) are available on the compute node, but the scripts also work for any other NVIDIA GPU. 

| NVIDIA Architecture        | Cards                                   | Supported Sm and Gencode Variations |
|:---------------------------|:----------------------------------------|:------------------------------------|
| Fermi (CUDA 3.2 until 8)   | GeForce 400, 500, 600, GT-630           | `SM_20` `compute_30`                |
| Kepler(CUDA 5 until 10)    | GeForce 700, GT-730                     | `SM_30` `compute_30`                |
|                            | Tesla K40                               | `SM_35` `compute_35`                |
|                            | Tesla K80                               | `SM_37` `compute_37`                |
| Maxwell (CUDA 6 until 11)  | Tesla/Quadro M                          | `SM_50` `compute_50`                |
|                            | Quadro M6000, GeForce 900,              | `SM_52` `compute_52`                |
|                            | GTX-970, GTX-980, GTX Titan-X           |                                     |
|                            | Jetson TX1/Tegra X1,                    | `SM_53` `compute_53`                |
|                            | Drive CX/PX, Jetson Nano                |                                     |
| Pascal (>= CUDA 8)         | Quadro GP100, Tesla P100, DGX-1         | `SM_60` `compute_60`                |
|                            | GTX 1080/1070/1060/1050/1030/1010       | `SM_61` `compute_61`                |
|                            | Titan Xp, Tesla P40, Tesla P4           |                                     |
|                            | iGPU on Drive PX2, Tegra(Jetson) TX2    | `SM_62` `compute_62`                |
| Volta (>= CUDA 9)          | **Tesla V100**, DGX-1, GTX1180,         | `SM_70` `compute_70`                |
|                            | Titan V, Quadro GV100                   |                                     |
|                            | Jetson AGX Xavier, Drive AGX Pegasus    | `SM_72` `compute_72`                |
|                            | Xavier NX                               |                                     |
| Turing (>= CUDA 10)        | GTX 1660, RTX 20X0 (X=6/7/8), Titan RTX|| `SM_75` `compute_75`                |
|                            | Quadro RTX 4000/5000/6000/8000,         |                                     |
|                            | Tesla T4                              |                                     |
| Ampere (>= CUDA 11.1)      | A100, GA100, DGX-A100                 | `SM_80` `compute_80`                |
|                            | GA10X cards, RTX 30X0 (X=5/6/7/8/9)   | `SM_86` `compute_86`                |

## Run the Application
Note that to successfully build this docker image and the necessary libraries/packages used for PageRank, you will
need sudo access on the machine you are doing this work. Otherwise, the container image will fail to build.

There are 5 steps to take to run ResNet-50 successfully. 
1. Download the ImageNet data set from [this link](https://image-net.org/download-images). We do not provide the data set in this artifact repo because it is so large. 
2. Update lines 28 and 29 in `run-resnet.sh` to provide the directory where the training data set and validation data set is located on your machine.
3. Run `sudo docker build -t resnet_image .`
4. Run `sudo docker run --gpus all resnet_image`
5. Move data output by profiler (nvprof) from container to local directory in this repository - see below. 

There will be 4 csv files and 1 txt file output by the profiler (nvprof), which contains kernel information, GPU SM frequency, power, and temperature. These files will be stored in the docker container by default. To access these files, you will have to copy them using `docker cp` (step 5) to the directory of your choice (we recommend `../out/`).

```
sudo docker create -ti --name dummy resnet_image bash
<Returns Container ID c_id>
sudo docker cp <c_id>:/sec5a/*.csv ../out/.
sudo docker rm -f dummy``
```

## Build and Run Without Docker
There are the steps to take to run BERT Pretraining using shell scripts:
1. Setup your environment. For our purposes we setup a Conda environment and separately installed Pytorch 1.9.0. Note that the steps for creating a Conda environment will change depending on the machine and software stack available. Many systems come with PyTorch Conda environments so it is recommended to clone the provided environment and use that instead.
```
$ conda create -n {ENV_NAME} python=3.8
$ conda activate {ENV_NAME}
$ conda env update --name {ENV_NAME} --file environment.yml
$ pip install -r requirements.txt
```

Install NVIDIA APEX. Note this step requires `nvcc` and may fail if done on systems without a GPU (i.e. you may need to install on a compute node).
```
$ git clone https://github.com/NVIDIA/apex
$ cd apex
$ pip install -v --disable-pip-version-check --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./
```
2. Download the dataset and configuration files by running the `scripts/create-datasets.sh` with the appropriate flags which downloads and encodes the Wikipedia English corpus (example below). This may take a couple of hours.
```
$ ./scripts/create_datasets.sh --output <DATA_DIR> --nproc 8 --download --no-books --format --encode --encode-type bert
```
3. Update line 8 in `scripts/run-pretraining-lamb.sh' to provide the directory where the encoded training dataset is located on your machine. (e.g. <DATA_DIR>/encoded/sequences_lowercase_max_seq_len_512_next_seq_task_true)
4. Update line 17 in `config/bert_large_uncased_config.json` to provide the correct path to the vocab.txt that was also downloaded as part of Step 1 (e.g. <DATA_DIR>/download/google_pretrained_weights/uncased_L-24_H-1024_A-16/vocab.txt).
5. Run `chmod u+x scripts/run-pretraining-lamb.sh scripts/launch-pretraining.sh`.
6. Run `scripts/run-pretraining-lamb.sh`.

You will find a few output files in `in this directory`:
  - `bert_*.csv`: contains kernel information, GPU SM frequency, power, and temperature. There will be one csv file per GPU (e.g., if you trained on 4 GPUs, there will be 4 csv files).