import subprocess
import time
import csv
from pathlib import Path

DATA_DIR = Path.home() / "pq-project" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def run_openssl_cmd(cmd, iterations=5):
    times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t1 = time.perf_counter()
        times.append(t1 - t0)
    avg = sum(times) / len(times)
    return avg

def main():
    rows = []

    rows.append({
        "family": "classical",
        "algorithm": "RSA-2048",
        "operation": "keygen",
        "avg_time_s": run_openssl_cmd(["openssl", "genrsa", "2048"])
    })

    rows.append({
        "family": "classical",
        "algorithm": "RSA-4096",
        "operation": "keygen",
        "avg_time_s": run_openssl_cmd(["openssl", "genrsa", "4096"])
    })

    rows.append({
        "family": "classical",
        "algorithm": "ECDSA-P256",
        "operation": "keygen",
        "avg_time_s": run_openssl_cmd(["openssl", "ecparam", "-name", "prime256v1", "-genkey"])
    })

    out_file = DATA_DIR / "classical.csv"
    with out_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {out_file}")

if __name__ == "__main__":
    main()

