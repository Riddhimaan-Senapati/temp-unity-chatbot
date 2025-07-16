# Full Database Test Results - claude-4-sonnet

**Test Timestamp:** 20250630_154254

**Model ID:** `us.anthropic.claude-sonnet-4-20250514-v1:0`

## Summary Metrics

- **Total Queries:** 27
- **Threads Processed:** 16
- **Total Response Time:** 289.190 seconds
- **Average Response Time:** 10.711 seconds
- **Total Input Tokens:** 225,950
- **Total Output Tokens:** 11,903
- **Total Tokens:** 237,853
- **Average Tokens/Second:** 822.48
- **Total Cost:** $0.856395

---

## Detailed Responses by Thread

### Thread: Introduction

**Thread Summary:**
- Queries: 1
- Total Response Time: 10.660 seconds
- Average Response Time: 10.660 seconds
- Total Cost: $0.026025
- Average Tokens/Second: 656.57

#### Q1: What is the Unity HPC?

**Response:**

Unity is a collaborative, multi-institutional high-performance computing platform located at the Massachusetts Green High Performance Computing Center (MGHPCC) [[1]](https://docs.unity.rc.umass.edu/documentation/)[[2]](https://docs.unity.rc.umass.edu/). 

Unity is under active development and supports primarily research activities [[1]](https://docs.unity.rc.umass.edu/documentation/)[[2]](https://docs.unity.rc.umass.edu/). The partnering institutions currently include UMass Amherst, University of Rhode Island, UMass Dartmouth, UMass Lowell, UMass Boston, and Mount Holyoke College [[1]](https://docs.unity.rc.umass.edu/documentation/)[[2]](https://docs.unity.rc.umass.edu/).

As of late 2024, Unity is an over 25,000 core cluster based on Ubuntu 24.04 LTS and Slurm with a heterogeneous network containing ethernet and IB linked compute nodes [[3]](https://docs.unity.rc.umass.edu/about/). Unity hosts a variety of compute node architectures, with the majority being Intel or AMD x86-64 nodes, supplemented by a small number of ARM and Power9 nodes. Additionally, Unity contains approximately 1300 Nvidia GPUs, including over 100 A100, L40S, and V100 GPUs [[3]](https://docs.unity.rc.umass.edu/about/).

The platform also includes 1.5 PB high performance VAST storage for home, work, and scratch directories, and 2 PB storage from the New England Storage Exchange (NESE) [[3]](https://docs.unity.rc.umass.edu/about/).

**Query Metrics:**
- Response Time: 10.660 seconds
- Input Tokens: 6,580
- Output Tokens: 419
- Total Tokens: 6,999
- Tokens/Second: 39.31
- Input Cost: $0.019740
- Output Cost: $0.006285
- Total Cost: $0.026025

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/](https://docs.unity.rc.umass.edu/documentation/)
- [https://docs.unity.rc.umass.edu/](https://docs.unity.rc.umass.edu/)
- [https://docs.unity.rc.umass.edu/about/](https://docs.unity.rc.umass.edu/about/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/](https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/](https://docs.unity.rc.umass.edu/documentation/get-started/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/hpc-resources/](https://docs.unity.rc.umass.edu/documentation/get-started/hpc-resources/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/](https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)

---

### Thread: Unity basics

**Thread Summary:**
- Queries: 2
- Total Response Time: 32.720 seconds
- Average Response Time: 16.360 seconds
- Total Cost: $0.079638
- Average Tokens/Second: 620.11

#### Q1: How do I access Unity?

**Response:**

There are multiple ways to connect to and access Unity [[2]](https://docs.unity.rc.umass.edu/documentation/help/faq/):

## Primary Connection Methods:

1. **Unity OnDemand** - This is the simplest and most convenient method because it allows you to login through your browser [[2]](https://docs.unity.rc.umass.edu/documentation/help/faq/). Unity OnDemand allows you to sign in using your organization's identity provider, so you don't need to install SSH, configure SSH, or set up any public and private keys [[3]](https://docs.unity.rc.umass.edu/documentation/connecting/ondemand/).

2. **SSH Connection** - This is the most traditional method, especially for experienced Command Line Interface (CLI) users. SSH connection allows you to connect to Unity in your terminal [[2]](https://docs.unity.rc.umass.edu/documentation/help/faq/).

3. **Visual Studio Code Desktop** - You can connect to Unity using the Remote-SSH feature, which is useful for users that prefer to use VS Code as their editor [[2]](https://docs.unity.rc.umass.edu/documentation/help/faq/).

4. **PuTTY** - This is a convenient way to connect to Unity that is available to Windows users [[2]](https://docs.unity.rc.umass.edu/documentation/help/faq/).

## Getting Started with Unity OnDemand:
To access Unity through OnDemand:
1. Login to Unity OnDemand with your organization's identity provider
2. From the top menu, click "Shell"
3. In the dropdown menu, click "Unity Shell Access" [[3]](https://docs.unity.rc.umass.edu/documentation/connecting/ondemand/)

The Unity platform provides both graphical and command-line methods for connecting to login and compute nodes [[1]](https://docs.unity.rc.umass.edu/documentation/connecting/).

**Query Metrics:**
- Response Time: 10.350 seconds
- Input Tokens: 5,635
- Output Tokens: 460
- Total Tokens: 6,095
- Tokens/Second: 44.43
- Input Cost: $0.016905
- Output Cost: $0.006900
- Total Cost: $0.023805

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/connecting/](https://docs.unity.rc.umass.edu/documentation/connecting/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/connecting/ondemand/](https://docs.unity.rc.umass.edu/documentation/connecting/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/connecting/ssh/](https://docs.unity.rc.umass.edu/documentation/connecting/ssh/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/connecting/vscode/](https://docs.unity.rc.umass.edu/documentation/connecting/vscode/)
- [https://docs.unity.rc.umass.edu/documentation/connecting/ssh/](https://docs.unity.rc.umass.edu/documentation/connecting/ssh/)
- [https://docs.unity.rc.umass.edu/about/](https://docs.unity.rc.umass.edu/about/)
- [https://docs.unity.rc.umass.edu/documentation/connecting/vscode/](https://docs.unity.rc.umass.edu/documentation/connecting/vscode/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/](https://docs.unity.rc.umass.edu/documentation/managing-files/)

---

#### Q2: What resources are available on Unity?

**Response:**

Based on the provided documentation, here are the Unity cluster's CPU, GPU, memory, and storage specifications:

## CPU Resources

Unity offers a wide variety of CPU configurations [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/):

**Intel CPUs:**
- Intel Xeon Gold series (5118, 6126, 6148, 6240, 6248R, 6526Y, etc.)
- Intel Xeon Platinum series (8352Y, 8480+)
- Intel Xeon Silver series (4214R, 4215R, 4116)
- Core counts ranging from 8 to 192 cores per node [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

**AMD CPUs:**
- AMD EPYC series (7402, 7502, 7543, 7702, 7763, 9654)
- AMD Ryzen Threadripper 1900X
- Core counts up to 192 cores (AMD EPYC 9654) [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

**ARM CPUs:**
- NVIDIA Grace Hopper Superchip (72 cores)
- Neoverse-N1 (80 cores) [[6]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

**POWER9 CPUs:**
- POWER9 processors with altivec support (32-40 cores) [[3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

## GPU Resources

Unity provides extensive GPU options [[10]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/):

**NVIDIA GPUs Available:**
- **GeForce Series:** GTX TITAN X, GTX 1080 Ti, RTX 2080, RTX 2080 Ti
- **Tesla Series:** M40 (24GB), V100 (16GB/32GB variants), A100 (40GB/80GB variants)
- **Professional Series:** Quadro RTX 8000 (48GB VRAM)
- **Latest Generation:** H100 (80GB), L40S (48GB), A40 (48GB), A16 (16GB), L4 (23GB)
- **Grace Hopper Superchip:** GH200 with 80-102GB VRAM [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

**Compute Capabilities:** Range from sm_52 to sm_90, supporting various CUDA features [[9]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/)

## Memory Specifications

**RAM Configurations:**
- **Low Memory:** 30GB - 180GB per node
- **Medium Memory:** 250GB - 500GB per node  
- **High Memory:** 1000GB - 2000GB per node
- **Ultra High Memory:** Up to 1510GB (AMD EPYC 9654 nodes) [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

**GPU Memory (VRAM):**
- Ranges from 8GB to 102GB depending on GPU model
- High-end options include A100 (80GB), H100 (80GB), and GH200 (102GB) [[10]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

## Network and Storage Features

**Network Capabilities:**
- 10 Gbps, 25 Gbps, 40 Gbps, and 100 Gbps Ethernet options
- InfiniBand (IB) networking available on many nodes for high-performance interconnects [[9]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/)

**Resource Selection Guidance:**
Unity recommends selecting appropriate resources based on your workload requirements [[4]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/):
- Choose CPU nodes based on RAM requirements
- Select less powerful GPUs when possible (M40, A40, V100, L40S) to improve scheduling
- Only request multiple GPUs if your code can use them efficiently

The cluster uses SLURM for job scheduling and resource allocation, with various partitions available for different job types and durations [[4]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/).

**Query Metrics:**
- Response Time: 22.370 seconds
- Input Tokens: 13,091
- Output Tokens: 1,104
- Total Tokens: 14,195
- Tokens/Second: 49.35
- Input Cost: $0.039273
- Output Cost: $0.016560
- Total Cost: $0.055833

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

---

### Thread: Tricky GPU error, driver/update problem

**Thread Summary:**
- Queries: 3
- Total Response Time: 26.110 seconds
- Average Response Time: 8.703 seconds
- Total Cost: $0.104412
- Average Tokens/Second: 1179.01

#### Q1: Could you help me with the error I am getting? (ials-gpu007: error: Failed to get device handle for GPU 7: Unknown Error). There is a problem with this GPU too: (ials-gpu008: error: Failed to get device handle for GPU 1: Unknown Error).

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

When you contact the help desk, please make sure to include:
- The exact commands you were running when the error occurred
- The complete error messages you received
- Details about your environment (which modules were loaded, partition used, etc.)
- What you were trying to accomplish

This will help the support team diagnose and resolve the GPU device handle errors you're experiencing on the ials-gpu nodes.

**Query Metrics:**
- Response Time: 5.430 seconds
- Input Tokens: 10,589
- Output Tokens: 156
- Total Tokens: 10,745
- Tokens/Second: 28.71
- Input Cost: $0.031767
- Output Cost: $0.002340
- Total Cost: $0.034107

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/gpu_summary/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/gpu_summary/)
- [https://docs.unity.rc.umass.edu/documentation/help/asking-questions/](https://docs.unity.rc.umass.edu/documentation/help/asking-questions/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

---

#### Q2: Is Unity Team able to detect these errors automatically, or shall I report all errors I encounter?

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Query Metrics:**
- Response Time: 3.260 seconds
- Input Tokens: 8,465
- Output Tokens: 70
- Total Tokens: 8,535
- Tokens/Second: 21.45
- Input Cost: $0.025395
- Output Cost: $0.001050
- Total Cost: $0.026445

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/help/asking-questions/](https://docs.unity.rc.umass.edu/documentation/help/asking-questions/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/help/asking-questions/](https://docs.unity.rc.umass.edu/documentation/help/asking-questions/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/](https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

---

#### Q3: Okay, thanks for the info. I got this other error on an A100 node (gpu023) from job 34002652. The script ran fine when I added --exclude gpu023.
/usr/local/lib/python3.8/dist-packages/torch/cuda/__init__.py:52: UserWarning: CUDA initialization: Unexpected error from cudaGetDeviceCount(). Did you run some cuda functions before calling NumCudaDevices() that might have already set an error? Error 802: system not yet initialized (Triggered internally at /pytorch/c10/cuda/CUDAFunctions.cpp:109.)
  return torch._C._cuda_getDeviceCount() > 0
...
    assert torch.cuda.is_available()
AssertionError:

**Response:**

Based on the provided context, here are some troubleshooting steps for CUDA initialization errors and GPU availability issues with A100 nodes:

## Common GPU Errors and Solutions

**CUDA Initialization/Out of Memory Errors:**
If you're encountering CUDA errors like `CUDA_ERROR_OUT_OF_MEMORY` or `torch.cuda.OutOfMemory`, this means that a GPU with more available VRAM may be necessary, or that the code being run should be modified to reduce the memory usage. For machine learning models running out of memory, try reducing the batch size or ensuring your data management is optimized [[2]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

## A100 GPU Specifications

Unity has several A100 GPU nodes available [[3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/):

- **gpu[013-021]**: 9 nodes with 8x NVIDIA Tesla A100 (80 GB VRAM each)
- **gpu[022-024]**: 3 nodes with 8x NVIDIA Tesla A100 (80 GB VRAM each)
- **gpu042**: 1 node with 1x NVIDIA Tesla A100 (80 GB VRAM)

## Requesting A100 GPUs with Job Exclusion

To request exclusive access to an A100 node, you can use:

```bash
#!/bin/bash
#SBATCH -p gpu-preempt
#SBATCH -t 02:00:00
#SBATCH --gpus=1
#SBATCH --constraint=a100
#SBATCH --exclusive
```

The `--exclusive` flag ensures you get an entire node [[4]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/nvlink/). For A100 nodes specifically, most have NVSwitch, so all GPUs are linked to each other at the same speed, and gpu[013-024] are connected with Infiniband for low-latency networking [[4]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/nvlink/).

## Troubleshooting GPU Issues

To diagnose GPU problems:

1. **Check GPU availability**: Add this command to your scripts to find out which GPU is being used:
   ```bash
   nvidia-smi -L
   ```

2. **Monitor GPU processes**: Use `nvidia-smi pmon` to view ongoing GPU processes [[7]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

3. **Use nvitop**: For an interactive view of ongoing processes for NVIDIA GPUs [[7]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

## Environment Setup

Make sure you're loading the appropriate CUDA modules:
```bash
module load cuda/12.6
module load cudnn/8.9.7.29-12-cuda12.6
```

When using multiple GPUs on a node, be sure to use the Slurm variable `SLURM_GPUS_ON_NODE` to ensure that ALL allocated GPUs on a node can be accessed by your software [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

**Query Metrics:**
- Response Time: 17.420 seconds
- Input Tokens: 10,725
- Output Tokens: 779
- Total Tokens: 11,504
- Tokens/Second: 44.71
- Input Cost: $0.032175
- Output Cost: $0.011685
- Total Cost: $0.043860

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/nvlink/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/nvlink/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/gpu_summary/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/gpu_summary/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

---

### Thread: Vague question, needs more info from user

**Thread Summary:**
- Queries: 3
- Total Response Time: 33.700 seconds
- Average Response Time: 11.233 seconds
- Total Cost: $0.097110
- Average Tokens/Second: 801.13

#### Q1: Hi there, I'm getting CUDA_HOME not existing error when utilizing gpu in sbatch for models. Could someone guide me on how best to resolve this issue?

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

However, based on the provided context, I can share some general guidance about GPU setup on Unity. When setting up GPU environments, it's important to load the appropriate CUDA modules. For example, when setting up a TensorFlow GPU environment, the documentation shows loading specific modules [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/):

```
module load conda/latest
module load cuda/12.6
module load cudnn/8.9.7.29-12-cuda12.6
```

The documentation also mentions that "A version of CUDA will typically be required to be loaded for most GPU jobs because it allows access to the NVIDIA compiler suite (nvcc, nvfortran) and the NVIDIA GPU profiling tool (nsys)" and recommends checking "which version(s) of cuda are compatible with the software that is being used" [[2]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

You can list available CUDA versions using `module spider cuda` [[2]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

**Query Metrics:**
- Response Time: 9.800 seconds
- Input Tokens: 10,097
- Output Tokens: 327
- Total Tokens: 10,424
- Tokens/Second: 33.37
- Input Cost: $0.030291
- Output Cost: $0.004905
- Total Cost: $0.035196

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/gpu_summary/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/gpu_summary/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/)

---

#### Q2: How to do load cuda module in my sbatch script?

**Response:**

Based on the provided context, here's how to load a CUDA module in an sbatch script and work with CUDA environment variables:

## Loading CUDA Module in sbatch Script

To load a CUDA module in your sbatch script, add the module load command after your SBATCH parameters [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/):

```bash
#!/bin/bash
#SBATCH -c 4 # Number of Cores per Task
#SBATCH --mem=8192 # Requested Memory
#SBATCH -p gpu # Partition
#SBATCH -G 1 # Number of GPUs
#SBATCH -t 01:00:00 # Job time limit
#SBATCH -o slurm-%j.out # %j = job ID

module load cuda/11.8
nvcc --version
```

## Available CUDA Versions

You can check available CUDA versions using [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/):
```bash
module spider cuda
```

The context shows examples of loading specific CUDA versions such as:
- `module load cuda/12.6` [[2]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- `module load cuda/11.8` [[5]](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)

## CUDA Compatibility Note

CUDA is NVIDIA's parallel computing platform and a version of CUDA will typically be required for most GPU jobs because it allows access to the NVIDIA compiler suite (nvcc, nvfortran) and the NVIDIA GPU profiling tool (nsys) [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/). Be sure to check which version(s) of CUDA are compatible with the software that you are using [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

The provided context doesn't include specific information about setting the CUDA_HOME environment variable, but it does show how to load CUDA modules which would typically set up the necessary environment variables for CUDA usage.

**Query Metrics:**
- Response Time: 11.980 seconds
- Input Tokens: 7,510
- Output Tokens: 517
- Total Tokens: 8,027
- Tokens/Second: 43.17
- Input Cost: $0.022530
- Output Cost: $0.007755
- Total Cost: $0.030285

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/software/conda/](https://docs.unity.rc.umass.edu/documentation/software/conda/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)
- [https://docs.unity.rc.umass.edu/documentation/software/conda/](https://docs.unity.rc.umass.edu/documentation/software/conda/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/)
- [https://docs.unity.rc.umass.edu/documentation/software/venv/](https://docs.unity.rc.umass.edu/documentation/software/venv/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/slurm/](https://docs.unity.rc.umass.edu/documentation/jobs/slurm/)

---

#### Q3: Should I add at the start of every sbatch script?

**Response:**

Based on the provided context, I can clarify how modules and sbatch work together for job submission:

**Module loading is not automatically required for every sbatch job**, but it depends on what your job needs to do. Here's how it works:

## Module Loading in Batch Jobs

When you submit a batch job using sbatch, you need to load any required modules **within your batch script**, not before running the sbatch command. For example:

```bash
#!/bin/bash
#SBATCH -c 4
#SBATCH --mem=8192
#SBATCH -p gpu
#SBATCH -G 1
#SBATCH -t 01:00:00
#SBATCH -o slurm-%j.out

module load cuda/11.8
nvcc --version
```

In this example, the `module load cuda/11.8` command is included within the batch script itself [[1]](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/).

## Different Examples from the Context

The context shows various scenarios:

1. **CUDA example**: Uses `module load cuda/11.8` within the batch script [[1]](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)

2. **R example**: Uses `module load r-rocker-ml-verse/4.4.0+apptainer` within the batch script [[4]](https://docs.unity.rc.umass.edu/documentation/tools/r/)

3. **Other examples**: Some batch scripts don't load any modules if they don't need special software [[5]](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/)

## Key Points

- **sbatch** is the command used to submit batch jobs to the Slurm scheduler [[1]](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)
- Modules should be loaded **inside** your batch script, not before running sbatch
- You only need to load modules that your specific job requires
- The batch script runs in its own environment, so modules loaded in your login session won't carry over

**Query Metrics:**
- Response Time: 11.920 seconds
- Input Tokens: 8,048
- Output Tokens: 499
- Total Tokens: 8,547
- Tokens/Second: 41.87
- Input Cost: $0.024144
- Output Cost: $0.007485
- Total Cost: $0.031629

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/slurm/](https://docs.unity.rc.umass.edu/documentation/jobs/slurm/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/](https://docs.unity.rc.umass.edu/documentation/jobs/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/)

---

### Thread: Pytorch GPU OOM

**Thread Summary:**
- Queries: 1
- Total Response Time: 16.810 seconds
- Average Response Time: 16.810 seconds
- Total Cost: $0.034260
- Average Tokens/Second: 501.84

#### Q1: Hi team, I'm getting the following error at some point in my experiments in job 34418381. I'm not sure how to change my configurations to resolve it. Could I get some help with this?
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 2.00 GiB. GPU 0 has a total capacity of 11.91 GiB of which 406.38 MiB is free. Including non-PyTorch memory, this process has 11.51 GiB memory in use. Of the allocated memory 11.18 GiB is allocated by PyTorch, and 219.44 MiB is reserved by PyTorch but unallocated. If reserved but unallocated memory is large try setting PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True to avoid fragmentation. See documentation for Memory Management (https://pytorch.org/docs/stable/notes/cuda.html#environment-variables)

**Response:**

Based on the error message you're encountering, this is a common "Out of Memory" error that occurs when using GPUs [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/). The error `torch.cuda.OutOfMemory` means that a GPU with more available VRAM may be necessary, or that the code being run should be modified to reduce the memory usage [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

Here are several approaches to resolve this issue:

## Immediate Solutions:

1. **Reduce batch size**: For machine learning models running out of memory, try reducing the batch size or ensuring your data management is optimized [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

2. **Try the PyTorch suggestion**: The error message suggests setting `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` to avoid fragmentation.

## Request a GPU with More VRAM:

Your current job appears to be using a GPU with ~12GB VRAM (likely a GTX 1080 Ti or RTX 2080 Ti). Consider requesting a GPU with more memory:

- **RTX 8000**: 48GB VRAM using `--constraint=rtx8000` [[10]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- **A40**: 48GB VRAM using `--constraint=a40` [[10]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- **A100-80GB**: 80GB VRAM using `--constraint=a100-80g` [[10]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- **L40S**: 48GB VRAM using `--constraint=l40s` [[10]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

## Monitor GPU Usage:

To better understand your memory usage, you can monitor your GPU with:
- `nvidia-smi` to view ongoing GPU processes [[2]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- `nvitop` for an interactive view of ongoing processes for NVIDIA GPUs [[2]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

## Choose the Right GPU:

To reduce time spent waiting in the queue, select the least powerful GPU that can run your code, as the choice is typically limited by the amount of available GPU memory [[8]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/). The large VRAM GPUs are often in high demand, so be prepared for your jobs to spend some time in the queue [[8]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

You can check current GPU availability using the `unity-slurm-gpu-usage` command to see which GPUs are currently idle [[7]](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/).

**Query Metrics:**
- Response Time: 16.810 seconds
- Input Tokens: 7,690
- Output Tokens: 746
- Total Tokens: 8,436
- Tokens/Second: 44.39
- Input Cost: $0.023070
- Output Cost: $0.011190
- Total Cost: $0.034260

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

---

### Thread: Gpu crash

**Thread Summary:**
- Queries: 1
- Total Response Time: 5.120 seconds
- Average Response Time: 5.120 seconds
- Total Cost: $0.025245
- Average Tokens/Second: 1551.37

#### Q1: I was running an interactive job with srun and suddenly got these errors:
slurmstepd-gypsum-gpu182: error: NVML: Failed to get usage(15): GPU is lost
slurmstepd-gypsum-gpu182: error: NVML: Failed to get Compute running process count(15): GPU is lost
Not sure what that means, and I'm unable to cancel the job 30185792

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

The provided context contains information about GPU usage monitoring, job submission, and general troubleshooting, but it doesn't include specific guidance for NVML errors or situations where GPUs are reported as "lost" by the system.

**Query Metrics:**
- Response Time: 5.120 seconds
- Input Tokens: 7,825
- Output Tokens: 118
- Total Tokens: 7,943
- Tokens/Second: 23.05
- Input Cost: $0.023475
- Output Cost: $0.001770
- Total Cost: $0.025245

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/slurm/](https://docs.unity.rc.umass.edu/documentation/jobs/slurm/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/slurm/](https://docs.unity.rc.umass.edu/documentation/jobs/slurm/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/slurm/](https://docs.unity.rc.umass.edu/documentation/jobs/slurm/)

---

### Thread: Issues figuring out how to acquire resources for test runs

**Thread Summary:**
- Queries: 2
- Total Response Time: 32.840 seconds
- Average Response Time: 16.420 seconds
- Total Cost: $0.083529
- Average Tokens/Second: 661.60

#### Q1: Good evening,
I'm having issues figuring out how I can acquire resources for my test runs.
I'm trying to run the llama3 70b model that we have locally. I believe that I need 500G of memory on GPU for that job but every time I attempt to run a job with these requests it goes pending for such a long time. I need to run multiple runs in one session to be able to troubleshoot my code and make changes in one working session.
Is there a chance that I can fix my request somehow to get quicker results? Or is that just how it goes when using this much resources.
I don't mind sharing the batch script I'm running if that might help.

**Response:**

Based on the provided documentation, I can help you understand the GPU resource situation and provide some suggestions for getting quicker results with your Llama3 70b model runs.

**Current GPU Resources with High VRAM:**

Looking at the available GPU resources [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/), the GPUs with the highest VRAM are:
- **NVIDIA GH200**: 102GB VRAM (constraint: `gh200`)
- **NVIDIA A100-SXM4-80GB**: 80GB VRAM (constraint: `a100` or `a100-80g`)
- **NVIDIA A40**: 48GB VRAM (constraint: `a40`)
- **NVIDIA L40S**: 48GB VRAM (constraint: `l40s`)
- **Quadro RTX 8000**: 48GB VRAM (constraint: `rtx8000`)

**Why Your Jobs Are Pending So Long:**

The documentation explains that "large vram GPUs are often in high demand. Be prepared for your jobs to spend some time in the queue before being able to launch" [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/). Since you need 500GB of GPU memory, you'd likely need multiple high-end GPUs, which increases queue time significantly.

**Suggestions to Get Quicker Results:**

1. **Use Interactive Jobs for Development**: For troubleshooting and making changes in one session, consider using interactive jobs with `salloc` [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/):
   ```bash
   salloc -p gpu-preempt -t 02:00:00 --gpus=a100:6 --mem=64G
   ```

2. **Try GPU-Preempt Partition**: For jobs requiring less than 2 hours, use the `gpu-preempt` partition [[3]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/). Note that jobs may be preempted after 2 hours if higher priority jobs need the resources [[4]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/).

3. **Use Multiple GPU Constraints**: You can specify multiple GPU options to increase your chances of getting resources faster [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/):
   ```bash
   #SBATCH --constraint=a100|gh200
   ```

4. **Monitor Available Resources**: Use the helper script to see current GPU availability [[2]](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/):
   ```bash
   unity-slurm-gpu-usage
   ```

5. **Consider Resource Optimization**: The documentation emphasizes requesting "the minimum necessary resources to avoid wasting compute power" [[3]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/). You might want to:
   - Test if your model can work with fewer GPUs or less memory
   - Use model quantization or other optimization techniques
   - Run scaling analysis to determine optimal resource allocation

**Reality Check:**
Unfortunately, when requesting very high amounts of GPU resources (500GB VRAM would require 6+ A100-80GB or 5+ GH200 GPUs), long queue times are expected due to resource scarcity and high demand [[1]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/).

Would you like to share your batch script? That might help identify if there are any optimizations possible in your resource requests.

**Query Metrics:**
- Response Time: 19.250 seconds
- Input Tokens: 7,703
- Output Tokens: 872
- Total Tokens: 8,575
- Tokens/Second: 45.30
- Input Cost: $0.023109
- Output Cost: $0.013080
- Total Cost: $0.036189

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/slurm/](https://docs.unity.rc.umass.edu/documentation/jobs/slurm/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

---

#### Q2: What difference is it to use a model that exists locally rather than use one that's online? It must be quicker to run, correct?

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

However, I can provide some general information about GPU memory (VRAM) available on Unity that might be helpful for your model considerations:

Unity offers various GPU options with different VRAM capacities [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/)[[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/):

**Available VRAM Options:**
- 8 GB VRAM: Available on RTX 2080 GPUs [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- 11 GB VRAM: Available on GTX 1080 Ti and RTX 2080 Ti GPUs [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- 16 GB VRAM: Available on Tesla V100 and A16 GPUs [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- 24 GB VRAM: Available on Tesla M40 and L4 GPUs [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- 32 GB VRAM: Available on some Tesla V100 configurations [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- 40 GB VRAM: Available on A100-PCIE-40GB GPUs [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- 48 GB VRAM: Available on Quadro RTX 8000, A40, and L40S GPUs [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- 80 GB VRAM: Available on A100-SXM4-80GB and H100 GPUs [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- 102 GB VRAM: Available on GH200 GPUs [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)

You can use constraints like `--constraint=vram40` or `--constraint=a100-80g` to request specific GPU types with adequate memory for your models [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/).

**Query Metrics:**
- Response Time: 13.590 seconds
- Input Tokens: 12,495
- Output Tokens: 657
- Total Tokens: 13,152
- Tokens/Second: 48.35
- Input Cost: $0.037485
- Output Cost: $0.009855
- Total Cost: $0.047340

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

---

### Thread: Disk usage

**Thread Summary:**
- Queries: 4
- Total Response Time: 42.980 seconds
- Average Response Time: 10.745 seconds
- Total Cost: $0.117036
- Average Tokens/Second: 741.09

#### Q1: I am trying to check my disk usage quota - but dont know if its full

**Response:**

To check your disk usage quota on Unity, you can use the `df` (disk free) command to see how much space you're using and have available [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

Here's how to check your quota usage:

```bash
$ df -h ~
```

This will show you output similar to:
```
Filesystem     Size  Used Avail Use% File
vast2:/home     50G   29G   22G  58%    ~
```

In this example, you can see that 58% of the 50GB home directory quota is being used, with 22GB still available [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

If you want to identify which specific files are taking up space in your directories, you can use the `du` (disk usage) command:

```bash
$ du -sh ~/.cache/*
```

This will show you the size of different subdirectories and help you identify what's consuming your storage [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

For an interactive way to explore your directory tree and see what's using space, you can use the `ncdu` command:

```bash
$ ncdu
```

This provides a visual interface where you can navigate through directories to see which folders and files are taking up the most space [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

If you find that your quota is full or nearly full, there are several strategies to reduce disk usage, including moving files to `/work` directories (which have larger quotas), deleting unnecessary files, or compressing directories [[3]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

**Query Metrics:**
- Response Time: 10.370 seconds
- Input Tokens: 7,413
- Output Tokens: 431
- Total Tokens: 7,844
- Tokens/Second: 41.55
- Input Cost: $0.022239
- Output Cost: $0.006465
- Total Cost: $0.028704

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)

---

#### Q2: Is it possible to add more space to it?

**Response:**

To request a storage quota increase on Unity HPC, you need to email **hpc@umass.edu** [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

Before making your request, here's what you should do:

1. **Check if you can reduce current storage use** - Review the storage management information to determine if you can reduce storage use without requiring expansion [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

2. **Determine your storage needs** using the provided flowchart and storage descriptions to identify:
   - Amount of storage needed
   - Duration required  
   - Type of storage needed [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

3. **For paid storage expansions**, you'll need to identify:
   - Appropriate institution payment method (e.g. speedtype, Chartfield string, etc.)
   - Name and email of the finance representative within your department [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

4. **Authorization requirement** - If you're not the PI (head) of your research group, the request must be done by your PI or with your PI's consent [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

**Available storage expansion options include:**
- **PI group work directories**: 1TB free tier, then available in 1TB increments on 6-month intervals
- **PI group project directories**: 5TB free tier (may vary by institution), then available in 5TB increments on 1-year intervals
- **NESE Tape storage**: Available in 10TB increments on 5-year intervals [[4]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

You can also write Unity storage purchases into grants - see their grant page for boilerplate information [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

**Query Metrics:**
- Response Time: 12.570 seconds
- Input Tokens: 7,220
- Output Tokens: 487
- Total Tokens: 7,707
- Tokens/Second: 38.73
- Input Cost: $0.021660
- Output Cost: $0.007305
- Total Cost: $0.028965

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)

---

#### Q3: Whats the timeline on project space?

**Response:**

Based on the provided context, PI group project directories can be expanded with the following timeline and duration specifications:

**Project Directory Storage Expansion Timeline & Duration:**

- **Purchasing availability:** Available in 5TB increments [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- **Purchase intervals:** 1 year intervals [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/) [[3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- **Maximum duration:** Up to 5 years at a time [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/) [[3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

**Free Tier Information:**
- **Base allocation:** 5TB (though URI and UMassD thresholds may vary) [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/) [[3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- **Free tier allocation:** Available upon request via the storage form [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/) [[3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

To request project directory storage expansion, you need to email hpc@umass.edu [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

**Query Metrics:**
- Response Time: 8.320 seconds
- Input Tokens: 7,962
- Output Tokens: 388
- Total Tokens: 8,350
- Tokens/Second: 46.64
- Input Cost: $0.023886
- Output Cost: $0.005820
- Total Cost: $0.029706

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)

---

#### Q4: Was just wondering if there was a faster way to move large files? than just using mv?

**Response:**

For transferring large files to Unity, there are several methods available, with some being more suitable for large file transfers than others:

**Best Options for Large Files:**

1. **Globus** - This is specifically mentioned as useful for large file transfers between Globus endpoints, including your personal computer with Globus Connect [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

2. **rsync** - This is excellent for large files and offers several advantages:
   - Good for recurring tasks and synchronizing files over a network [[2]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
   - Comes with useful options like the `-tlp` flags that preserve timestamps, relative links, and permissions [[2]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
   - For directories: `rsync -rtlp DIRECTORY_NAME unity:~` [[2]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)

3. **Command-line tools** like scp and rsync are noted as good for quick work via the command line [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

**Less Suitable for Large Files:**

- **Unity OnDemand** - While it's the most intuitive interface, it specifically "can't transfer large files" [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

**Important Note on Transfer Speeds:**
The documentation mentions that "uploading files using American residential internet is typically very slow. UMass Amherst has a fiber line going directly to MGHPCC to improve speeds" [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/), so your location may affect transfer performance.

All transfer methods require SSL encrypted connections, and FileZilla and command-line methods require setting up SSH keys [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

**Query Metrics:**
- Response Time: 11.720 seconds
- Input Tokens: 7,467
- Output Tokens: 484
- Total Tokens: 7,951
- Tokens/Second: 41.31
- Input Cost: $0.022401
- Output Cost: $0.007260
- Total Cost: $0.029661

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/](https://docs.unity.rc.umass.edu/documentation/managing-files/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)

---

### Thread: R env

**Thread Summary:**
- Queries: 1
- Total Response Time: 11.140 seconds
- Average Response Time: 11.140 seconds
- Total Cost: $0.027639
- Average Tokens/Second: 656.82

#### Q1: Hi all! Hopefully an easy question - I'm trying to help someone install some R software in an apptainer container. Their software comes with a file called Modular.R that should install everything it needs. I'm not sure yet if this will play nicely with apptainer (optimistic), but so far I can't even figure out how to run it.

If I load the r-rocker-ml-verse/4.4.0+apptainer module and then run "Rscript /path/to/Modular.R" it will run, but Modular.R will fail because /usr/... of course isn't writable. When I try to run "Rscript /path/to/Modular.R" within a .def file, however, it gives me a "cannot open file 'Modular.R': No such file or directory" error. I can copy the exact path from the error message and it opens the correct file, so the path is specified correctly. What am I doing wrong here?

**Response:**

Based on the provided context, the issue you're encountering is related to file access within the Apptainer container build environment. When building a container with a `.def` file, the build process runs in an isolated environment where external files (like your `Modular.R` script) are not accessible by default.

Here are a few approaches to resolve this:

**Option 1: Copy the file into the container during build**
In your `.def` file, you can copy the `Modular.R` file into the container and then run it. Here's an example based on the context provided [[1]](https://docs.unity.rc.umass.edu/documentation/software/):

```
Bootstrap: docker
From: rocker/ml-verse:4.4.0

%files
    /path/to/Modular.R /opt/Modular.R

%post
    apt-get -y update
    # Install any system dependencies if needed
    
    # Run your R script
    Rscript /opt/Modular.R
```

**Option 2: Include the R commands directly in the %post section**
Instead of running an external script, you could include the R installation commands directly in the `%post` section of your `.def` file, similar to the example shown in the context [[1]](https://docs.unity.rc.umass.edu/documentation/software/):

```
%post
    apt-get -y update
    # Install R packages directly
    Rscript -e 'install.packages("pak")'
    Rscript -e 'pak::pak(c("package1", "package2"))'
```

The key issue is that during the container build process (`apptainer build`), the build environment doesn't have access to your host filesystem paths unless you explicitly copy files into the container using the `%files` section of the definition file.

If you need to install packages that require write access to system directories, this should work within the `%post` section since the build process runs with the necessary privileges to modify the container's filesystem.

**Query Metrics:**
- Response Time: 11.140 seconds
- Input Tokens: 6,843
- Output Tokens: 474
- Total Tokens: 7,317
- Tokens/Second: 42.56
- Input Cost: $0.020529
- Output Cost: $0.007110
- Total Cost: $0.027639

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/software/](https://docs.unity.rc.umass.edu/documentation/software/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/software/renv/](https://docs.unity.rc.umass.edu/documentation/software/renv/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/software/modules/](https://docs.unity.rc.umass.edu/documentation/software/modules/)
- [https://docs.unity.rc.umass.edu/documentation/software/renv/](https://docs.unity.rc.umass.edu/documentation/software/renv/)
- [https://docs.unity.rc.umass.edu/documentation/software/renv/](https://docs.unity.rc.umass.edu/documentation/software/renv/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/](https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/)

---

### Thread: Slash error

**Thread Summary:**
- Queries: 1
- Total Response Time: 4.510 seconds
- Average Response Time: 4.510 seconds
- Total Cost: $0.025518
- Average Tokens/Second: 1776.94

#### Q1: Good afternoon.
I'm having this error on a batch run:
slurmstepd-uri-cpu014: error: execve(): /var/spool/slurm/slurmd/job37168102/slurm_script: Not a directory

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

The error you're encountering appears to be related to Slurm's execution of your batch script, but the provided documentation doesn't contain troubleshooting information for this specific "Not a directory" error with the slurm_script file.

**Query Metrics:**
- Response Time: 4.510 seconds
- Input Tokens: 7,891
- Output Tokens: 123
- Total Tokens: 8,014
- Tokens/Second: 27.26
- Input Cost: $0.023673
- Output Cost: $0.001845
- Total Cost: $0.025518

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/monitoring/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/slurm/](https://docs.unity.rc.umass.edu/documentation/jobs/slurm/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/](https://docs.unity.rc.umass.edu/documentation/jobs/sbatch/arrays/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/salloc/](https://docs.unity.rc.umass.edu/documentation/jobs/salloc/)

---

### Thread: Stored datasets

**Thread Summary:**
- Queries: 2
- Total Response Time: 8.370 seconds
- Average Response Time: 4.185 seconds
- Total Cost: $0.056958
- Average Tokens/Second: 2167.50

#### Q1: Hi I have a question related to accessing the datasets stored on the unity
I am currently using VideoMAE-V2, and I see that on unity under the documentations section: https://docs.unity.rc.umass.edu/documentation/datasets/ai/videomae/, it mentions that the dataset is available to use. But I could not find it when I go to /datasets/ai/opengvlab
Could you please let me know if I am missing anything?
I am particularly looking for Kinetics400 dataset.
Thanks in Advance.

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

The provided documentation mentions that Unity has datasets available and references a /datasets directory [[9]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/), but it doesn't contain specific details about the VideoMAE or Kinetics400 dataset locations or access procedures that you're asking about.

**Query Metrics:**
- Response Time: 4.700 seconds
- Input Tokens: 6,666
- Output Tokens: 141
- Total Tokens: 6,807
- Tokens/Second: 29.98
- Input Cost: $0.019998
- Output Cost: $0.002115
- Total Cost: $0.022113

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/about/](https://docs.unity.rc.umass.edu/about/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/about/](https://docs.unity.rc.umass.edu/about/)
- [https://docs.unity.rc.umass.edu/documentation/](https://docs.unity.rc.umass.edu/documentation/)
- [https://docs.unity.rc.umass.edu/documentation/help/asking-questions/](https://docs.unity.rc.umass.edu/documentation/help/asking-questions/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/contributing/](https://docs.unity.rc.umass.edu/documentation/contributing/)

---

#### Q2: Over here: /datasets/ai/opengvlab/hub/models--OpenGVLab--VideoMAEv2-Large/ is it the pre-trained model?
I was wondering if I can access the large datasets like Kinetics400 dataset if stored on unity?

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Query Metrics:**
- Response Time: 3.670 seconds
- Input Tokens: 11,265
- Output Tokens: 70
- Total Tokens: 11,335
- Tokens/Second: 19.09
- Input Cost: $0.033795
- Output Cost: $0.001050
- Total Cost: $0.034845

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/about/](https://docs.unity.rc.umass.edu/about/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

---

### Thread: Contact for storage space

**Thread Summary:**
- Queries: 1
- Total Response Time: 9.110 seconds
- Average Response Time: 9.110 seconds
- Total Cost: $0.026559
- Average Tokens/Second: 825.14

#### Q1: Who can I contact regarding increasing storage space for my PI account and the associated costs regarding it?

**Response:**

For storage expansion requests and information about associated costs, you should contact the Unity help desk at **hpc@umass.edu** [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

When requesting additional storage, you'll need to:

1. Check the storage management information to determine if you can reduce storage use without expansion [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
2. Determine the amount, duration, and type of storage needed using their flowchart and storage descriptions [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
3. If you're requesting storage expansion that requires payment, identify the appropriate institution payment method (e.g. speedtype, Chartfield string, etc.) and provide the name and email of the finance representative within your department [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
4. Note that if you're not the PI (head) of your research group, the request must be done by your PI or with your PI's consent [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

You can also write Unity storage purchases into grants - see their grant page for grant boilerplate and information [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

**Query Metrics:**
- Response Time: 9.110 seconds
- Input Tokens: 7,183
- Output Tokens: 334
- Total Tokens: 7,517
- Tokens/Second: 36.66
- Input Cost: $0.021549
- Output Cost: $0.005010
- Total Cost: $0.026559

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/getting-access/](https://docs.unity.rc.umass.edu/documentation/getting-access/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)

---

### Thread: Scratch space

**Thread Summary:**
- Queries: 1
- Total Response Time: 11.030 seconds
- Average Response Time: 11.030 seconds
- Total Cost: $0.030456
- Average Tokens/Second: 751.77

#### Q1: Good morning, How do I know if I have scratch space or apply for some?

**Response:**

Good morning! Based on the provided documentation, scratch space on Unity is available to all users and doesn't require a separate application process. Here's what you need to know:

## Scratch Space Availability
Scratch space is available through Unity's **HPC Workspace tool** with a 50TB soft cap, and no purchasing is necessary [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/) [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

## How to Create Scratch Space
You can create high-performance scratch space using the `ws_allocate` command. Here's how:

**Basic workspace creation:**
```bash
ws_allocate simple 14
```
This creates a workspace named "simple" for 14 days (maximum duration is 30 days) [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/).

**Check your existing workspaces:**
```bash
ws_list -v
```
This command will show you all your current workspaces with details like remaining time, creation date, and available extensions [[3]](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/).

## Key Features
- Maximum workspace duration: 30 days
- You can extend workspaces up to 5 times (increased from 3)
- Workspaces can be shared with other users or PI groups
- Email reminders can be set before expiration [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/) [[3]](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)

The scratch space is located at `/scratch` and uses high-performance SSD storage suitable for job I/O [[10]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

**Query Metrics:**
- Response Time: 11.030 seconds
- Input Tokens: 7,827
- Output Tokens: 465
- Total Tokens: 8,292
- Tokens/Second: 42.16
- Input Cost: $0.023481
- Output Cost: $0.006975
- Total Cost: $0.030456

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/salloc/](https://docs.unity.rc.umass.edu/documentation/jobs/salloc/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/](https://docs.unity.rc.umass.edu/documentation/jobs/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

---

### Thread: Upload large pkl files

**Thread Summary:**
- Queries: 1
- Total Response Time: 8.500 seconds
- Average Response Time: 8.500 seconds
- Total Cost: $0.025929
- Average Tokens/Second: 862.47

#### Q1: What is the best way to upload a really large .pkl file?

**Response:**

Based on the provided context, for uploading really large files like a .pkl file, **Globus** is the best option available on Unity [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

The documentation specifically states that "Globus is useful for large file transfers between Globus endpoints, including your personal computer with Globus Connect" [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/). 

Other methods have limitations for large files:
- Unity OnDemand "is the most intuitive interface, but can't transfer large files" [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/)
- FileZilla and command-line tools (scp, rsync) are mentioned but not specifically recommended for large file transfers

Additionally, the documentation notes that "uploading files using American residential internet is typically very slow. UMass Amherst has a fiber line going directly to MGHPCC to improve speeds" [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/), so using the campus network connection when possible would also help with large file transfers.

To use Globus, you would need to set up Globus Connect on your personal computer and transfer between Globus endpoints [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

**Query Metrics:**
- Response Time: 8.500 seconds
- Input Tokens: 7,003
- Output Tokens: 328
- Total Tokens: 7,331
- Tokens/Second: 38.57
- Input Cost: $0.021009
- Output Cost: $0.004920
- Total Cost: $0.025929

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/](https://docs.unity.rc.umass.edu/documentation/managing-files/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/filezilla/](https://docs.unity.rc.umass.edu/documentation/managing-files/filezilla/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- [https://docs.unity.rc.umass.edu/documentation/software/ondemand/jupyterlab-ondemand/](https://docs.unity.rc.umass.edu/documentation/software/ondemand/jupyterlab-ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/filezilla/](https://docs.unity.rc.umass.edu/documentation/managing-files/filezilla/)
- [https://docs.unity.rc.umass.edu/documentation/software/ondemand/jupyterlab-ondemand/](https://docs.unity.rc.umass.edu/documentation/software/ondemand/jupyterlab-ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/software/ondemand/](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)

---

### Thread: Average wait time

**Thread Summary:**
- Queries: 1
- Total Response Time: 11.420 seconds
- Average Response Time: 11.420 seconds
- Total Cost: $0.038046
- Average Tokens/Second: 952.19

#### Q1: Hey, what's the average wait time on 500G of ram 4 GPU cores for 1 hour? Is there anything I can do to be able request more time to be able to work on and test my project?

**Response:**

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

However, I can provide some general guidance based on the available information about optimizing your job scheduling:

**For reducing queue times:**
- Use the `unity-slurm-gpu-usage` and `unity-slurm-node-usage` helper scripts to check current resource availability [[1]](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- Consider using less powerful GPUs if possible (e.g. M40, A40, V100, L40S) as recommended [[4]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- For jobs shorter than 4 hours, you can boost job priority by adding `--qos=short` to your job batch script [[5]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)

**For longer development/testing work:**
- For jobs requiring less than 2 hours, use preempt partitions (`--partition=gpu-preempt`) which typically have shorter queue times [[3]](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- For jobs longer than 2 days, you'll need to specify `-q long` [[4]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)

The documentation emphasizes that "time to solution is the sum of the time your job is waiting in the queue plus the time it takes to run it" and recommends finding a balance between resource allocation and queue time [[6]](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/).

**Query Metrics:**
- Response Time: 11.420 seconds
- Input Tokens: 10,422
- Output Tokens: 452
- Total Tokens: 10,874
- Tokens/Second: 39.60
- Input Cost: $0.031266
- Output Cost: $0.006780
- Total Cost: $0.038046

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/tools/gpus/](https://docs.unity.rc.umass.edu/documentation/tools/gpus/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/](https://docs.unity.rc.umass.edu/documentation/jobs/helper_scripts/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/gpu_summary/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/gpu_summary/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

---

### Thread: Install program to directory

**Thread Summary:**
- Queries: 2
- Total Response Time: 24.170 seconds
- Average Response Time: 12.085 seconds
- Total Cost: $0.058035
- Average Tokens/Second: 634.55

#### Q1: Hi, would it be possible for me to install this program on my work directory and any advice on how to go about it?

**Response:**

I can see that you're asking about installing a program on your work directory, but you haven't specified which program you'd like to install. However, I can provide some general guidance about work directories on Unity based on the available information.

Your work directory on Unity is located at `/work/pi_<your-pi-username>/<your-username>` and serves as the primary location for running cluster jobs [[5]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/). Work directories use high-performance SSD storage with a base quota of 1TB and are shared folders for all users in the PI group [[5]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

For software installation and environment management, the documentation mentions that Conda environments can be stored in work directories. Specifically, the following directories are automatically used if they exist: `/work/pi_<your-pi-username>/.conda` and `/work/pi_<your-pi-username>/<your-username>` [[2]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

I'm sorry, but the specific information about installing particular programs isn't available in the provided documents. For further assistance with software installation on Unity, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Query Metrics:**
- Response Time: 9.440 seconds
- Input Tokens: 7,060
- Output Tokens: 335
- Total Tokens: 7,395
- Tokens/Second: 35.48
- Input Cost: $0.021180
- Output Cost: $0.005025
- Total Cost: $0.026205

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/filezilla/](https://docs.unity.rc.umass.edu/documentation/managing-files/filezilla/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/filezilla/](https://docs.unity.rc.umass.edu/documentation/managing-files/filezilla/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/](https://docs.unity.rc.umass.edu/documentation/get-started/common-terms/)

---

#### Q2: Can I get the GUI to show up on the cluster?

**Response:**

Based on the provided context, Unity OnDemand offers several GUI and desktop solutions that eliminate the need for traditional X11 forwarding:

## Unity OnDemand Graphical Interface Options

Unity OnDemand provides **Batch Connect** as a way to run graphical applications, which "starts your software as a batch job, then connects you to your software through a VNC server. Anything that you could have run with X11 forwarding can now be run much faster and more easily through Batch Connect" [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/).

## Available Desktop and GUI Applications

Unity OnDemand includes several graphical applications and desktop environments:

- **Virtual Desktop Environment**: A general-purpose interactive desktop environment [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
- **VSCode**: Available through Batch Connect [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
- **JupyterLab**: Web-based interactive computational environment [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
- **Matlab**: Available as an interactive app [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
- **RStudio**: IDE for R programming [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
- **Mathematica**: Available through the platform [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
- **XFCE**: A general purpose interactive desktop environment [[7]](https://docs.unity.rc.umass.edu/documentation/help/faq/)

## How to Access GUI Applications

To run these graphical applications:

1. Go to Unity OnDemand and click the **My Interactive Sessions** icon from the top menu [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
2. Select an Interactive App from the side menu [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
3. Configure your resource requirements (CPU threads, time, GPUs) [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
4. Click **Launch** to submit your job [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
5. Once the job is running, click the connect button to access your application [[2]](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)

This approach provides a much more convenient alternative to traditional X11 forwarding for running graphical applications on the Unity cluster.

**Query Metrics:**
- Response Time: 14.730 seconds
- Input Tokens: 7,275
- Output Tokens: 667
- Total Tokens: 7,942
- Tokens/Second: 45.29
- Input Cost: $0.021825
- Output Cost: $0.010005
- Total Cost: $0.031830

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/software/ondemand/](https://docs.unity.rc.umass.edu/documentation/software/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/software/ondemand/jupyterlab-ondemand/](https://docs.unity.rc.umass.edu/documentation/software/ondemand/jupyterlab-ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/connecting/ondemand/](https://docs.unity.rc.umass.edu/documentation/connecting/ondemand/)
- [https://docs.unity.rc.umass.edu/about/](https://docs.unity.rc.umass.edu/about/)
- [https://docs.unity.rc.umass.edu/documentation/tools/r/](https://docs.unity.rc.umass.edu/documentation/tools/r/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/nvlink/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/features/nvlink/)
- [https://docs.unity.rc.umass.edu/documentation/jobs/ondemand/](https://docs.unity.rc.umass.edu/documentation/jobs/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/nodes/)

---

