# Toolchest-hosted pricing and instance types

By default, Toolchest jobs run in Toolchest's managed AWS account. The prices below are for resources that you spawn by 
running Toolchest jobs. For information on running Toolchest in your own AWS account, see 
[Running Toolchest in your AWS account](./running-toolchest-in-your-aws-account.md)

Toolchest Hosted Cloud pricing starts with a free allowance and moves to incremental billing, scaling as your usage 
grows.

Per-minute billing starts when the Toolchest instance begins executing, and stops immediately when a run finishes. You 
can say goodbye to paying for idling cloud instances.

## Free tier

### Compute

| Service     | Free tier      | What can you run?                                 |
| :---------- | :------------- | :------------------------------------------------ |
| vCPU        | 50 vCPU-hours  | A run that lasts 2 hours with 25 vCPUs.           |
| RAM         | 100 GB-hours   | A run that lasts 2 hours with 50 GB of RAM        |
| Disk        | 2 TB-hour      | A run that lasts 2 hours with 1 TB of disk space. |
| Invocations | 50 invocations | 50 runs                                           |

### Files

| Service                         | Free tier | What can you run?                                                                  |
| :------------------------------ | :-------- | :--------------------------------------------------------------------------------- |
| Input and output files          | 100 GB    | A run with 40 GB of transferred input files and 60 GB of transferred output files. |
| High speed reference DB storage | 50 GB/mo  | A custom reference database for Kraken 2 that's 50 GB.                             |

## Growth pricing

### Compute

| Service    | Cost                 | Billing increment                     |
| :--------- | :------------------- | :------------------------------------ |
| vCPU       | $0.084 per vCPU-hour | Per minute, with a one minute minimum |
| RAM        | $0.016 per GB-hour   | Per minute, with a one minute minimum |
| Disk       | $0.009 per TB-hour   | Per minute, with a one minute minimum |
| Invocation | $0.10 per invocation | Per run                               |

### Files

| Service                               | Cost           | Billing increment                  |
| :------------------------------------ | :------------- | :--------------------------------- |
| Input and output files                | $0.1 per GB    | Per GB                             |
| High speed reference database storage | $2.4 per GB-mo | Per month, with at least one month |

!!! note "Input and output file pricing includes network data transfer and temporary storage"
    Every input and output file includes free transfer to and from Toolchest infrastructure. The files are cached for one week (7 days) after the run is initialized.

### Example pricing with a Toolchest-hosted bioinformatics tool, Kraken 2

A Kraken 2 run with 2 GB of input files, 16 vCPUs, and 128 GB of RAM with 128 GB of disk space runs for 5 minutes. It produces 1 GB of output files, for a total of 3 GB of input and output files. This costs:

- 3 GB of input and output files \* $0.1 per GB = $0.3
- 16 vCPUs \* 0.08 hours \* $0.084 per vCPU-hour = $0.10752
- 128 GB of RAM \* 0.08 hours \* $0.016 per RAM GB-hour = $0.16384
- 0.125 TB of disk \* 0.08 hours \* $0.009 per TB-hour = $0.00009
- 1 invocation = $0.10

For a total of **$0.67**

### Example pricing with a custom Python script

A custom Python3 script with 40 GB of input files, 32 vCPUs, and 64 GB of RAM with 256 GB of disk space runs for 30 minutes. It produces 10 GB of output files, for a total of 50 GB of input and output files. This costs:

- 50 GB of input and output files \* $0.1 per GB = $5
- 32 vCPUs \* 0.5 hours \* $0.084 per vCPU-hour = $1.344
- 64 GB of RAM \* 0.5 hours \* $0.016 per RAM GB-hour = $0.512
- 0.25 TB of disk \* 0.5 hours \* $0.009 per TB-hour = $0.001125
- 1 invocation = $0.10

For a total of **$6.96**


## Support

Every customer gets access to text-based support – including a shared Slack channel, email, and any other async way 
that you can think of talking to us.

We offer synchronous support, and SLAs for support and infrastructure availability, too.

## Custom plans

If you're a business with unique needs (e.g. high volume, a non-standard business model, or very large files), we can 
build a custom plan for you.