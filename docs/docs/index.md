# Toolchest

If you're ready to start building, head straight to [Installation](getting-started/installation.md), 
[Running Bioinformatics Packages with Toolchest](./getting-started/running-bioinformatics-on-toolchest.md), or 
[Custom Python Functions and Containers](./getting-started/python-functions-and-containers.md).

## What does Toolchest do?

Toolchest is an open source library for running computational biology software in the cloud.  For software that has 
reference databases, Toolchest comes with pre-built reference DBs on our high-speed cloud database store – or you can 
add your own.

Toolchest handles input and output file transfer as well as cloud resource provisioning. That means you can use the 
Toolchest library from anywhere you write Python, including Jupyter notebooks or a Python function – on your computer or 
in the cloud.

## Who should use Toolchest?

If you:

- use bioinformatics software that runs on the command line, but you write code in Python
- have functions that need more resources than your laptop, but you don't want to manage your own cloud infrastructure
- handle a lot of data

then you should try Toolchest!

## What doesn't Toolchest solve?

- Pipelining (see Prefect, Dagster, Nextflow, or Snakemake)
- Data versioning or management

## Why Toolchest?

- You can scale instantly with Toolchest; Toolchest is built on top of AWS
- You don't need an AWS account! Toolchest jobs run in our own AWS account by default
- Cloud resources are spun up and down immediately, maximizing efficiency and reducing idling resources
