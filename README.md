# Train-of-Four Monitoring Interpreter

Educational software for interpreting measured **train-of-four (TOF) twitch count**, **post-tetanic count (PTC)**, and **quantitative TOF ratio**. The browser interpreter and Python module implement explicit, testable monitoring categories based on the 2023 ASA practice guidelines.

> **Educational / research demonstration only.** Not a medical device or clinically validated decision-support system. It does **not** prescribe sugammadex, neostigmine, or other drugs; assess all criteria for extubation; or substitute for direct quantitative neuromuscular monitoring. Do not input identifiable patient data.

## Browser application

Open [`web/index.html`](web/index.html) locally in a modern browser, or use GitHub Pages **after deployment has been enabled and verified**. No build step, backend, account, or network request is required for evaluation. Enter TOF count (0–4), PTC if count is zero, and measured TOF ratio if count is four. The result may be exported as a JSON file.

The browser app does not store inputs, send measurements to a service, or use analytics. The only external links are optional references that open when clicked.

## Python CLI

Python 3.10–3.12 is exercised in CI. Python 3.9 is supported by the package metadata.

```bash
python -m pip install -e .
neuromuscular-blockade-train-of-four-engine tof --count 4 --ratio 0.92
neuromuscular-blockade-train-of-four-engine tof --count 0 --ptc 2
neuromuscular-blockade-train-of-four-engine tof --count 2
```

The direct Python API is `neuromuscular_blockade_train_of_four_agent.tof.interpret_tof(count, ptc=None, ratio=None)`. Invalid or incompatible combinations raise `ValueError`. Missing clinically relevant measurements remain **indeterminate** rather than being inferred.

| Observations | Educational interpretation |
|---|---|
| TOF 0/4; PTC 0 | Complete block |
| TOF 0/4; PTC ≥1 | Deep block |
| TOF 1–3/4 | Moderate block |
| TOF 4/4; quantitative ratio <0.4 | Shallow block |
| TOF 4/4; ratio 0.4 to <0.9 | Minimal block |
| TOF 4/4; ratio ≥0.9 | Quantitative recovery threshold met |
| TOF 0 without PTC, or TOF 4 without ratio | Indeterminate |

These are monitoring *categories*, not treatment orders. The ASA guideline recommends quantitative monitoring at the **adductor pollicis** and TOF ratio **≥0.9** before extubation, alongside appropriate clinical assessment.

## Legacy modules

The repository also retains older, separately implemented generic-metric demos: root `cli.py`, `tof_sentinel.py`, `agents/`, `enrichment.py`, and the packaged `audit` / `batch` commands. **Their numeric limits (for example 20, 25, and 12) are synthetic demonstration thresholds, not ASA TOF criteria.** They do not implement reliable medication dosing or clinical escalations. Compatibility is maintained where practical while the verified TOF interpretation is provided separately.

```bash
python -m pip install -e ".[api,test]"
python -m pytest -q
node --test web/app.test.mjs
python cli.py audit --task-id EXAMPLE --primary 12
```

## Optional legacy REST API and Docker

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export TOF_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker compose up --build
```

The container binds to `127.0.0.1:8000` by default. `/health` and aggregated `/metrics` are public; `/api/audit`, `/api/chat`, and `/api/audit/logs` require the `X-API-Key` header. Without a configured private key, restricted requests fail closed. The server is a **legacy test interface**, not a clinical service.

Audit HMAC signatures cover an in-memory chain, **not a durable, independently archived audit record**. The limited pattern-based identifier checks are not comprehensive PHI de-identification or HIPAA compliance. Do not deploy publicly or submit real patient records.

## Implementation

- Browser: static HTML and ES module; no JavaScript package dependencies.
- Python: standard-library TOF classifier; optional Pydantic/ FastAPI legacy components.
- Tests: `pytest`, Node's built-in test runner, CI on Python 3.10–3.12.
- Deployment: a GitHub Pages workflow publishes the `web/` directory if repository Pages settings permit. The static app does not run Python; no Pyodide is necessary.

**Reference:** Thilen SR et al. *2023 American Society of Anesthesiologists Practice Guidelines for Monitoring and Antagonism of Neuromuscular Blockade*. Anesthesiology. 2023;138:13–41. [DOI:10.1097/ALN.0000000000004379](https://doi.org/10.1097/ALN.0000000000004379). [PubMed](https://pubmed.ncbi.nlm.nih.gov/36520073/).

## License

[MIT](LICENSE).
