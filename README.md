# Neuromuscular Blockade Train Of Four Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** ASA Neuromuscular Blockade Guidelines 2023, CAP / CLSI / ISO Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Neuromuscular Blockade Train Of Four Agent** is an advanced analytical and computational platform implementing Train-of-Four (TOF) Twitch Count & Sugammadex Reversal Agent. It monitors peripheral nerve stimulator twitch counts (0-4/4), post-tetanic counts (PTC), and calculates Sugammadex reversal dosing (2, 4, or 16 mg/kg).

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`TwitchCountEvaluatorAgent`**: Specialized Sub-Agent 1 for neuromuscular-blockade-train-of-four-agent
- **`SugammadexDosingAgent`**: Specialized Sub-Agent 2 for neuromuscular-blockade-train-of-four-agent
- **`NeostigmineGlycoPairingAgent`**: Specialized Sub-Agent 3 for neuromuscular-blockade-train-of-four-agent

### 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/neuromuscular-blockade-train-of-four-agent.git
cd neuromuscular-blockade-train-of-four-agent

# Install dependencies
pip install -e .

# Optional: Install web server dependencies
pip install fastapi uvicorn
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --task-id <value> --target <value> --primary <value> --secondary <value>
```

### Parameter Reference
- `--task-id`: Specifies input measurement or parameter value.
- `--target`: Specifies input measurement or parameter value.
- `--primary`: Specifies input measurement or parameter value.
- `--secondary`: Specifies input measurement or parameter value.
- `--critical`: Specifies input measurement or parameter value.
- `--status`: Specifies input measurement or parameter value.
- `--input`: Specifies input measurement or parameter value.
- `--output`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `case_id` | Parameter / observation metric | Required |
| `patient_synthetic_id` | Parameter / observation metric | Required |
| `metric_primary` | Parameter / observation metric | Required |
| `metric_secondary` | Parameter / observation metric | Required |
| `is_stat` | Parameter / observation metric | Required |
| `status_flag` | Parameter / observation metric | Required |

---

## 🛡️ Security Configuration

### Audit Secret Key

The HMAC-SHA256 audit trail requires a secret key for cryptographic signing. Configure it via environment variable:

```bash
export AUDIT_SECRET_KEY="your-secure-random-key-min-32-chars"
```

**⚠️ Important:** If `AUDIT_SECRET_KEY` is not set, an ephemeral random key will be generated at startup. This means:
- Audit trail integrity will be maintained within a single session
- Audit trail will NOT persist across restarts
- A runtime warning will be emitted

For production deployments, always set a persistent, securely-generated key.

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

### Docker
```bash
docker build -t neuromuscular-blockade-train-of-four-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-secure-key" neuromuscular-blockade-train-of-four-agent
```

### Docker Compose
```bash
# Set your audit key
export AUDIT_SECRET_KEY="your-secure-production-key"

# Launch
docker-compose up -d
```

---

## 📁 Project Structure

```
neuromuscular-blockade-train-of-four-agent/
├── agents/                    # Core agent modules
│   ├── __init__.py
│   ├── api.py                 # FastAPI REST endpoints
│   ├── base.py                # Security, PHI guard, audit trail
│   ├── learning.py            # Bayesian calibration engine
│   ├── llm_factory.py         # LLM provider factory
│   ├── metrics.py             # Prometheus metrics collector
│   ├── models.py              # Pydantic data models
│   ├── streamer.py            # WebSocket telemetry broadcaster
│   ├── supervisor.py          # Master coordinator orchestrator
│   └── workers.py             # Specialized domain workers
├── tests/                     # Test suite
│   ├── test_enrichment.py
│   └── test_neuromuscular_blockade_train_of_four_agent.py
├── cli.py                     # Main CLI entry point
├── simulator.py               # High-throughput simulation
├── enrichment.py              # Feature enrichment engines
├── tof_sentinel.py            # Alternative TOF implementation
├── neuromuscular_blockade_train_of_four_agent/  # Secondary package
├── web/index.html             # Operations console
├── Dockerfile                 # Container build
├── docker-compose.yml         # Compose configuration
├── openapi_spec.json          # OpenAPI 3.1 specification
├── pyproject.toml             # Project metadata
└── README.md                  # This file
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
