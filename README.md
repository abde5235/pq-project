# Post-Quantum Cryptography Benchmarks

This project benchmarks classical cryptography (RSA/ECC via OpenSSL) and
post-quantum cryptography (Kyber KEM and ML-DSA signatures via liboqs/liboqs-python)
on Ubuntu.

## Structure

- `classical/`
  - `classical_bench.py` – measures RSA/ECC keygen times using OpenSSL.
  - `pqc_bench.py` – measures Kyber + ML-DSA KEM/signature times using liboqs.
  - `make_plots.py` – generates bar charts from CSV data.

- `data/` *(ignored in git)* – generated CSVs (classical.csv, pqc.csv).
- `graphs/` *(ignored in git)* – generated PNG plots.
- `wireshark/` *(ignored in git)* – TLS handshake captures and screenshots.
- `venv/` *(ignored in git)* – Python virtual environment.

## How to run

```bash
python classical/classical_bench.py
python classical/pqc_bench.py
python classical/make_plots.py
