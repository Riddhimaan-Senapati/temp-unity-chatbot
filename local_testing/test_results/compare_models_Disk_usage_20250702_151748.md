# Model Comparison Results - Disk usage

**Test Timestamp:** 20250702_151748

## Summary Metrics

- **Thread Tested:** Disk usage
- **Models Tested:** 4
- **Questions per Model:** 4
- **Total Queries (All Models):** 16

### Best Performance

- **Fastest Model:** llama-4-maverick (1.847s avg)
- **Cheapest Model:** llama-4-maverick ($0.007370 total)
- **Highest Tokens/Second:** llama-4-maverick (3666.17)

## Model Performance Comparison

| Model | Avg Response Time (s) | Total Cost ($) | Avg Tokens/Sec | Total Input Tokens | Total Output Tokens |
|-------|----------------------|----------------|----------------|-------------------|--------------------|
| claude-4-sonnet | 9.415 | $0.108108 | 804.67 | 28,871 | 1,433 |
| claude-3.5-haiku | 11.425 | $0.028182 | 659.50 | 28,867 | 1,272 |
| nova-premier | 4.635 | $0.083001 | 1591.15 | 28,575 | 925 |
| llama-4-maverick | 1.847 | $0.007370 | 3666.17 | 25,904 | 1,189 |

---

## Detailed Responses by Model

### Model: claude-4-sonnet

**Model ID:** `us.anthropic.claude-sonnet-4-20250514-v1:0`

**Model Summary:**
- Queries: 4
- Total Response Time: 37.660 seconds
- Average Response Time: 9.415 seconds
- Total Cost: $0.108108
- Average Tokens/Second: 804.67
- Total Input Tokens: 28,871
- Total Output Tokens: 1,433

#### Q1: I am trying to check my disk usage quota - but dont know if its full

**Response:**

To check your disk usage quota on Unity, you can use the `df` (disk free) command to see how much space you're using and how much is available. Here's how to check your quota usage:

**Check your quota usage:**
Use the `df -h ~` command to check your home directory quota [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/):

```
$ df -h ~
Filesystem      Size  Used Avail Use% File
vast2:/home      50G   29G   22G  58%    ~
```

This shows you the total size, used space, available space, and percentage used.

**Check which files are using up your space:**
If you want to see which files are taking up the most space, use the `du` (disk usage) command [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/):

```
$ du -sh ~/.cache/*
```

**Interactive directory exploration:**
For a more interactive way to explore your directory usage, you can use the `ncdu` command [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/):

```
ncdu
```

This provides a visual interface where you can navigate with arrow keys and see which directories are using the most space.

**Understanding the quota limits:**
Your home directory has a quota of 50GB [[7]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/). If you're approaching or exceeding this limit, you may experience issues with software and need to free up space by moving files to your `/work` directory (which has a 1TB quota) or deleting unnecessary files [[3]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

**Query Metrics:**
- Response Time: 10.520 seconds
- Input Tokens: 7,413
- Output Tokens: 431
- Total Tokens: 7,844
- Tokens/Second: 40.96
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

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

However, I can share some general information about storage expansion on Unity that might be helpful:

Unity offers several storage expansion options [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/):

- **PI group work directories**: 1TB free tier, with purchasing available in 1TB increments on 6-month intervals, up to 3 years at a time
- **PI group project directories**: 5TB free tier (URI, UMassD threshold may vary), with purchasing available in 5TB increments on 1-year intervals, up to 5 years at a time  
- **Scratch space**: 50TB soft cap with no purchasing necessary

To request additional storage on Unity, you can email hpc@umass.edu [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/). If you're not the PI (head) of your research group, this must be done by your PI or with your PI's consent [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

There's also a helpful storage expansion flowchart available to help determine what type of storage you need [[3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

**Query Metrics:**
- Response Time: 10.240 seconds
- Input Tokens: 7,222
- Output Tokens: 369
- Total Tokens: 7,591
- Tokens/Second: 36.04
- Input Cost: $0.021666
- Output Cost: $0.005535
- Total Cost: $0.027201

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/software/](https://docs.unity.rc.umass.edu/documentation/software/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)

---

#### Q3: Whats the timeline on project space?

**Response:**

Based on the provided context, project space has the following timeline characteristics:

**For purchasing project space:**
- Available in 5TB increments on 1 year intervals, up to 5 years at a time [[1]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

**For free tier project space:**
- 5TB is allocated upon request (though the threshold may vary for URI and UMassD) [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

**To request project space:**
- You need to email hpc@umass.edu [[4]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- Most campuses provide a base allocation free of charge to research groups upon request [[4]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- If you're not the PI (head) of your research group, the request must be done by your PI or with your PI's consent [[5]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)

The context doesn't specify how long it takes to process project space requests after submitting them via email.

**Query Metrics:**
- Response Time: 8.100 seconds
- Input Tokens: 7,450
- Output Tokens: 294
- Total Tokens: 7,744
- Tokens/Second: 36.29
- Input Cost: $0.022350
- Output Cost: $0.004410
- Total Cost: $0.026760

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)

---

#### Q4: Was just wondering if there was a faster way to move large files? than just using mv?

**Response:**

Based on the provided context, there are several methods mentioned for transferring files to Unity, but the context doesn't specifically compare the speed of `mv` versus other methods for moving files within the Unity filesystem.

However, the context does mention some relevant information about file transfers:

For uploading files to Unity, the context notes that **Globus is useful for large file transfers** between Globus endpoints [[3]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

The context also mentions that **Unity's VAST storage can be slow when it comes to handling large numbers of small files**, and recommends considering using **tmux or a batch job for large I/O operations** [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

For command-line file operations, the context mentions **rsync** as an option for "recurring tasks and synchronizing files over a network" [[9]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/), though this is in the context of uploading files to Unity rather than moving files within the Unity filesystem.

I'm sorry, but the specific information you're looking for about faster alternatives to `mv` for moving large files within Unity isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Query Metrics:**
- Response Time: 8.800 seconds
- Input Tokens: 6,786
- Output Tokens: 339
- Total Tokens: 7,125
- Tokens/Second: 38.51
- Input Cost: $0.020358
- Output Cost: $0.005085
- Total Cost: $0.025443

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/git-guide/](https://docs.unity.rc.umass.edu/documentation/get-started/git-guide/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/](https://docs.unity.rc.umass.edu/documentation/managing-files/)
- [https://docs.unity.rc.umass.edu/documentation/software/renv/](https://docs.unity.rc.umass.edu/documentation/software/renv/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/software/venv/](https://docs.unity.rc.umass.edu/documentation/software/venv/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)

---


### Model: claude-3.5-haiku

**Model ID:** `us.anthropic.claude-3-5-haiku-20241022-v1:0`

**Model Summary:**
- Queries: 4
- Total Response Time: 45.700 seconds
- Average Response Time: 11.425 seconds
- Total Cost: $0.028182
- Average Tokens/Second: 659.50
- Total Input Tokens: 28,867
- Total Output Tokens: 1,272

#### Q1: I am trying to check my disk usage quota - but dont know if its full

**Response:**

I can help you check your disk usage quota on the Unity HPC system. Here are a few methods you can use:

1. Check Quota Usage with df Command:
Use the `df` command to check the available space in your home directory:
```
$ df -h ~
```
[[Source 1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/) This will show you the total size, used space, available space, and percentage used for your home directory.

2. Check Specific File and Directory Usage with du Command:
To see which files or directories are taking up space, use the `du` command:
```
$ du -sh ~/.cache/*
```
[[Source 1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/) This will recursively show the size of each subdirectory in your .cache folder.

3. Interactive Directory Tree Exploration with ncdu:
For a more interactive way to explore your disk usage, use the `ncdu` command:
```
$ ncdu ~
```
[[Source 1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/) This provides a navigable interface to see which directories and files are consuming your disk space.

Note: Your home directory has a default quota of 50GB [[Source 7]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/). If you're running out of space, consider:
- Deleting unnecessary files
- Moving files to `/work` or `/project` directories
- Compressing large directories
- Requesting additional storage from your PI

Would you like help with any of these disk management strategies?

**Query Metrics:**
- Response Time: 12.280 seconds
- Input Tokens: 7,412
- Output Tokens: 398
- Total Tokens: 7,810
- Tokens/Second: 32.40
- Input Cost: $0.005930
- Output Cost: $0.001592
- Total Cost: $0.007522

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

Based on the context provided, here are the details about adding more space to a workspace:

For scratch space, the HPC Workspace tool provides some flexibility:

1. Extensions: [[Source 1]](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/) The number of extensions for scratch spaces has been increased from 3 to 5. You can use the `ws_extend` command to extend a workspace.

Example of extending a workspace:
```
username@login2:~$ ws_extend simple 30
Info: extending workspace. 
/scratch/workspace/username-simple 
remaining extensions : 2 
remaining time in days: 30
```

2. Maximum Duration: [[Source 1]](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/) The maximum duration for a workspace is 30 days, and you can extend it up to the available number of extensions.

3. Storage Capacity: [[Source 3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/) Scratch space has a 50T soft cap, and no purchasing is necessary.

If you need more permanent storage solutions, you have several options:
- PI group project directories
- Work directories
- Requesting additional storage by emailing hpc@umass.edu

For specific details about extending your workspace or storage needs, I recommend contacting the Unity HPC team at hpc@umass.edu.

**Query Metrics:**
- Response Time: 11.770 seconds
- Input Tokens: 7,221
- Output Tokens: 343
- Total Tokens: 7,564
- Tokens/Second: 29.13
- Input Cost: $0.005777
- Output Cost: $0.001372
- Total Cost: $0.007149

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/software/](https://docs.unity.rc.umass.edu/documentation/software/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)

---

#### Q3: Whats the timeline on project space?

**Response:**

Based on the provided context [[Source 4]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/), here are the details about project space:

1. Project directories are typically 5T for URI and UMass Dartmouth (though thresholds may vary).

2. Free Tier: Project directories are allocated upon request via a storage form.

3. Purchasing Options:
- Available in 5T increments
- Can be purchased for 1-year intervals
- Can be purchased up to 5 years at a time

To request project space, you should email hpc@umass.edu. Most campuses provide a base allocation free of charge to research groups upon request.

Additionally, the context notes that project directories are typically housed on the Northeast Storage Exchange (NESE)'s Disk Storage and are a cost-effective way to store data with good transfer speeds to Unity's high-performance storage.

**Query Metrics:**
- Response Time: 8.230 seconds
- Input Tokens: 7,449
- Output Tokens: 211
- Total Tokens: 7,660
- Tokens/Second: 25.63
- Input Cost: $0.005959
- Output Cost: $0.000844
- Total Cost: $0.006803

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)

---

#### Q4: Was just wondering if there was a faster way to move large files? than just using mv?

**Response:**

Based on the provided context, I can offer some insights about moving files on Unity:

[[Source 3]](https://docs.unity.rc.umass.edu/documentation/managing-files/) mentions several methods for file transfer, including:
1. Unity OnDemand
2. FileZilla
3. Globus
4. Command-line tools like scp and rsync

Specifically for large file transfers, [[Source 3]](https://docs.unity.rc.umass.edu/documentation/managing-files/) notes that:
- Unity OnDemand is not suitable for large files
- Globus is useful for large file transfers between Globus endpoints
- Command-line tools like rsync can be effective for file transfers

[[Source 1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/) also provides a helpful note: "Our VAST storage can be slow when it comes to handling large numbers of small files. Consider using tmux or a batch job for large I/O operations."

For the most efficient large file transfer, I recommend:
1. Using rsync (which can handle incremental transfers)
2. Using Globus for very large transfers
3. Considering a batch job for substantial I/O operations

If you need specific guidance on implementing these methods, I suggest contacting the Unity help desk at hpc@umass.edu for personalized assistance.

**Query Metrics:**
- Response Time: 13.420 seconds
- Input Tokens: 6,785
- Output Tokens: 320
- Total Tokens: 7,105
- Tokens/Second: 23.85
- Input Cost: $0.005428
- Output Cost: $0.001280
- Total Cost: $0.006708

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/git-guide/](https://docs.unity.rc.umass.edu/documentation/get-started/git-guide/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/](https://docs.unity.rc.umass.edu/documentation/managing-files/)
- [https://docs.unity.rc.umass.edu/documentation/software/renv/](https://docs.unity.rc.umass.edu/documentation/software/renv/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/software/venv/](https://docs.unity.rc.umass.edu/documentation/software/venv/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)

---


### Model: nova-premier

**Model ID:** `us.amazon.nova-premier-v1:0`

**Model Summary:**
- Queries: 4
- Total Response Time: 18.540 seconds
- Average Response Time: 4.635 seconds
- Total Cost: $0.083001
- Average Tokens/Second: 1591.15
- Total Input Tokens: 28,575
- Total Output Tokens: 925

#### Q1: I am trying to check my disk usage quota - but dont know if its full

**Response:**

To check your disk usage quota on Unity, you can use the `df` command. For example, to check the quota for your home directory, you would run:

```bash
df -h ~
```

This command will show you the total size, used space, available space, and the percentage of the quota used for your home directory [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

If you need to see which files are taking up the most space, you can use the `du` command. For example:

```bash
du -sh ~/.cache/*
```

This command will list the sizes of the directories and files within `~/.cache` [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

For more detailed information on managing disk quotas, you can refer to the [disk quota management documentation](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

**Query Metrics:**
- Response Time: 5.060 seconds
- Input Tokens: 7,401
- Output Tokens: 244
- Total Tokens: 7,645
- Tokens/Second: 48.19
- Input Cost: $0.018503
- Output Cost: $0.003050
- Total Cost: $0.021553

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

The context provided does not explicitly state whether it is possible to add more space to the HPC Workspace. However, it does mention that scratch space has a 50T soft cap and no purchasing is necessary [[3]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

If you need more storage beyond the scratch space, you should consider the following options:

1. **Move files to /work or /project directories**: These directories have larger quotas than the home directory [[9]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).
2. **Request additional storage**: If you need more storage, you can request it by emailing hpc@umass.edu. The request should include the amount, duration, and type of storage needed [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

For further assistance, you can reach out to the help desk at [hpc@umass.edu] or visit the community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Query Metrics:**
- Response Time: 5.220 seconds
- Input Tokens: 7,143
- Output Tokens: 276
- Total Tokens: 7,419
- Tokens/Second: 52.91
- Input Cost: $0.017857
- Output Cost: $0.003450
- Total Cost: $0.021308

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/software/](https://docs.unity.rc.umass.edu/documentation/software/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)

---

#### Q3: Whats the timeline on project space?

**Response:**

Answer: Project directories on Unity are available for 1-year intervals, with the option to purchase up to 5 years at a time [[5]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/). The base allocation is 5TB, and additional space can be purchased in 5TB increments [[5]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/). To request project space, email hpc@umass.edu [[4]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

**Query Metrics:**
- Response Time: 3.140 seconds
- Input Tokens: 7,233
- Output Tokens: 154
- Total Tokens: 7,387
- Tokens/Second: 48.99
- Input Cost: $0.018082
- Output Cost: $0.001925
- Total Cost: $0.020007

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)

---

#### Q4: Was just wondering if there was a faster way to move large files? than just using mv?

**Response:**

Answer: For moving large files efficiently on Unity, consider using `rsync` instead of `mv`. While `mv` works well for local moves, `rsync` offers advantages like:

- **Partial Transfers**: Only copies changed parts of files [[9]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- **Compression**: Reduces data size during transfer [[9]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- **Progress Tracking**: Shows transfer status [[9]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)

Example:  
`rsync -avz --progress SOURCE_FILE unity:DESTINATION_PATH`

For extremely large datasets, Globus is recommended for high-speed transfers between endpoints [[3]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

Note: Always test commands on small files first to avoid accidental data loss.

**Query Metrics:**
- Response Time: 5.120 seconds
- Input Tokens: 6,798
- Output Tokens: 251
- Total Tokens: 7,049
- Tokens/Second: 49.04
- Input Cost: $0.016995
- Output Cost: $0.003138
- Total Cost: $0.020133

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/git-guide/](https://docs.unity.rc.umass.edu/documentation/get-started/git-guide/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/](https://docs.unity.rc.umass.edu/documentation/managing-files/)
- [https://docs.unity.rc.umass.edu/documentation/software/renv/](https://docs.unity.rc.umass.edu/documentation/software/renv/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/software/venv/](https://docs.unity.rc.umass.edu/documentation/software/venv/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)

---


### Model: llama-4-maverick

**Model ID:** `us.meta.llama4-maverick-17b-instruct-v1:0`

**Model Summary:**
- Queries: 4
- Total Response Time: 7.390 seconds
- Average Response Time: 1.847 seconds
- Total Cost: $0.007370
- Average Tokens/Second: 3666.17
- Total Input Tokens: 25,904
- Total Output Tokens: 1,189

#### Q1: I am trying to check my disk usage quota - but dont know if its full

**Response:**

To check your disk usage quota, you can use the `df` (disk free) command. Here's an example of how to do it:
$ df -h ~
Filesystem      Size  Used Avail Use% Mounted on
vast2:/home     50G   29G   22G  58%   ~

This command will show you the amount of free space under the quota for your home directory [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

Additionally, you can use the `du` (disk usage) command to check which files are using up your space. For example:
$ du -sh ~/.cache/*
120M    ansible
19K     black
512     dconf
21M     epiphany
3.5K    fontconfig
353K    gstreamer-1.0
64K     gvfs-metadata
92M     mozilla
78M     pip
16M     rclone
1.0K    rstudio
255K    thumbnails

You can also use the `ncdu` (ncurses disk usage) command to explore your directory tree through an interactive interface [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

**Query Metrics:**
- Response Time: 1.530 seconds
- Input Tokens: 6,627
- Output Tokens: 265
- Total Tokens: 6,892
- Tokens/Second: 172.67
- Input Cost: $0.001590
- Output Cost: $0.000257
- Total Cost: $0.001848

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

To determine if it's possible to add more space, we need to understand the context of "it." Assuming "it" refers to a storage or workspace on the Unity HPC cluster, the answer can be derived from the provided context.

For a workspace created using HPC Workspace, the command `ws_extend` can be used to extend its duration [[1]](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/). However, the context does not explicitly mention increasing the storage space of a workspace, only extending its duration.

For storage options like PI group work directories or project directories, additional storage can be purchased in specific increments [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/). For example, PI group work directories can be expanded in 1T increments, and project directories can be expanded in 5T increments.

If "it" refers to a home directory or another specific storage location, the context suggests managing disk quotas by moving files, deleting unnecessary files, or compressing directories to reduce usage [[5]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)[[9]](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/).

To directly answer the question: if "it" refers to a workspace, you can extend its duration but the context doesn't directly support increasing its space. If "it" refers to storage like /work or /project, yes, more space can be added by purchasing additional storage.

For further assistance on managing or expanding storage, you can email hpc@umass.edu [[8]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

I'm sorry, but the specific information you're looking for isn't available in the provided documents. For further assistance, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Query Metrics:**
- Response Time: 2.760 seconds
- Input Tokens: 6,496
- Output Tokens: 404
- Total Tokens: 6,900
- Tokens/Second: 146.62
- Input Cost: $0.001559
- Output Cost: $0.000392
- Total Cost: $0.001951

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/software/](https://docs.unity.rc.umass.edu/documentation/software/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/](https://docs.unity.rc.umass.edu/documentation/help/troubleshooting/)

---

#### Q3: Whats the timeline on project space?

**Response:**

To determine the timeline for project space, we need to look at the purchasing options available. According to the provided context, PI group project directories have a free tier allocated upon request, and purchasing is available in 5T increments on 1-year intervals, up to 5 years at a time [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

Additionally, it is mentioned that storage purchasing via grants is also an option, and users can write Unity storage purchases into grants [[5]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

Therefore, the timeline for project space is as follows:
- Free tier: allocated upon request.
- Purchasing: available in 5T increments on 1-year intervals, up to 5 years at a time.


For more detailed information, you can refer to the storage documentation [[2]](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/).

**Query Metrics:**
- Response Time: 1.220 seconds
- Input Tokens: 6,601
- Output Tokens: 193
- Total Tokens: 6,794
- Tokens/Second: 157.99
- Input Cost: $0.001584
- Output Cost: $0.000187
- Total Cost: $0.001771

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/](https://docs.unity.rc.umass.edu/documentation/managing-files/hpc-workspace/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/help/faq/](https://docs.unity.rc.umass.edu/documentation/help/faq/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/partitions/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/](https://docs.unity.rc.umass.edu/documentation/get-started/quickstart/)

---

#### Q4: Was just wondering if there was a faster way to move large files? than just using mv?

**Response:**

You're looking for a faster way to move large files than using the `mv` command. While the provided context doesn't directly compare the speed of different file-moving commands, it does discuss alternatives for transferring files [[3]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

For large file transfers, you can consider using `rsync` instead of `mv` or `scp`. The `rsync` command is particularly useful for synchronizing files over a network and can be more efficient than `scp` for large files or directories because it can resume transfers and only copies the parts of files that have changed [[9]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/).

Here's an example of how to use `rsync` to move a directory:
```bash
rsync -rtlp DIRECTORY_NAME unity:~
```
This command preserves timestamps, relative links, and permissions [[9]](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/).

Additionally, for very large file transfers, using Globus is recommended as it is useful for large file transfers between Globus endpoints, including your personal computer with Globus Connect [[3]](https://docs.unity.rc.umass.edu/documentation/managing-files/).

I'm sorry, but the specific information on whether `rsync` is faster than `mv` for local file transfers isn't available in the provided context. For further assistance on optimizing file transfers, you can reach out to our help desk at [hpc@umass.edu] or visit our community page at [https://docs.unity.rc.umass.edu/contact/community/].

**Query Metrics:**
- Response Time: 1.880 seconds
- Input Tokens: 6,180
- Output Tokens: 327
- Total Tokens: 6,507
- Tokens/Second: 174.22
- Input Cost: $0.001483
- Output Cost: $0.000317
- Total Cost: $0.001800

**Sources (10):**
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/get-started/git-guide/](https://docs.unity.rc.umass.edu/documentation/get-started/git-guide/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/](https://docs.unity.rc.umass.edu/documentation/managing-files/)
- [https://docs.unity.rc.umass.edu/documentation/software/renv/](https://docs.unity.rc.umass.edu/documentation/software/renv/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/](https://docs.unity.rc.umass.edu/documentation/managing-files/quotas/)
- [https://docs.unity.rc.umass.edu/documentation/software/venv/](https://docs.unity.rc.umass.edu/documentation/software/venv/)
- [https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/](https://docs.unity.rc.umass.edu/documentation/cluster_specs/storage/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/](https://docs.unity.rc.umass.edu/documentation/managing-files/ondemand/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)
- [https://docs.unity.rc.umass.edu/documentation/managing-files/cli/](https://docs.unity.rc.umass.edu/documentation/managing-files/cli/)

---


