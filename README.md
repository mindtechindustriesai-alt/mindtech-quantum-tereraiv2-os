# MQOS TERERAI v2.1

**Africa's Quantum Operating System**

MindTech Industries · SA Patent 2026/05142

## Overview

MQOS TERERAI is a sovereign quantum orchestration backend providing:

- **Real CHSH verification** — IBM Kingston hardware + Qiskit Aer exact fallback
- **Multi-provider routing** — dynamic backend selection
- **Circuit compression** — reduces gate and qubit requirements
- **Error mitigation** — Zero-Noise Extrapolation
- **Efficient encoding** — amplitude encoding (N → log₂N)
- **Key management** — CSPRNG with rotation and revocation
- **Threat detection** — heuristic scoring with extensible interface

## Quick Start

```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
