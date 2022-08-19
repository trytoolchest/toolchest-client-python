from enum import Enum


class InstanceType(Enum):
    # Compute optimized, lists vCPUs, 1:2 vCPU to RAM ratio
    COMPUTE_2 = "compute-2"
    COMPUTE_4 = "compute-4"
    COMPUTE_8 = "compute-8"
    COMPUTE_16 = "compute-16"
    COMPUTE_32 = "compute-32"
    COMPUTE_48 = "compute-48"
    COMPUTE_64 = "compute-64"
    COMPUTE_96 = "compute-96"
    # General optimized, lists vCPUs, 1:4 vCPU to RAM ratio
    GENERAL_2 = "general-2"
    GENERAL_4 = "general-4"
    GENERAL_8 = "general-8"
    GENERAL_16 = "general-16"
    GENERAL_32 = "general-32"
    GENERAL_48 = "general-48"
    GENERAL_64 = "general-64"
    GENERAL_96 = "general-96"
    # Memory optimized, lists memory, 1:8 vCPU to RAM ratio
    MEMORY_16 = "memory-16"
    MEMORY_32 = "memory-32"
    MEMORY_64 = "memory-64"
    MEMORY_128 = "memory-128"
    MEMORY_256 = "memory-256"
    MEMORY_384 = "memory-384"
    MEMORY_512 = "memory-512"



