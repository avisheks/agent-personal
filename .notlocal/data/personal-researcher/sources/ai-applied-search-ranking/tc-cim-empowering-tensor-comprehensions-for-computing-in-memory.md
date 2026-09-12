---
title: "TC-CIM: Empowering Tensor Comprehensions for Computing-In-Memory"
source: "https://research.google/pubs/pub48845/"
ingestedAt: "2026-07-30T14:12:03Z"
---
## Abstract

Memristor-based, non-von-Neumann architectures performing tensor  
operations directly in memory are a promising approach to address the  
ever-increasing demand for energy-efficient, high-throughput hardware  
accelerators for Machine Learning (ML) inference. A major challenge  
for the programmability and exploitation of such  
Computing-In-Memory (CIM) architectures consists in the efficient mapping of tensor  
operations from high-level ML frameworks to fixed-function  
hardware blocks implementing in-memory computations.  
  
We demonstrate the programmability of memristor-based accelerators  
with TC-CIM, a fully-automatic, end-to-end compilation flow from  
Tensor Comprehensions, a mathematical notation for tensor  
operations, to fixed-function memristor-based hardware blocks.  
Operations suitable for acceleration are identified  
using Tactics, a declarative framework to describe  
computational patterns in a polyhedral representation.  
We evaluate our compilation flow on a  
system-level simulator based on Gem5, incorporating crossbar arrays of  
memristive devices. Our results show that TC-CIM reliably  
recognizes tensor operations commonly used in ML workloads across  
multiple benchmarks in order to offload these operations to the  
accelerator.