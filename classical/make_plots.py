import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Base directories
BASE_DIR = Path.home() / "pq-project"
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "graphs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
df_classical = pd.read_csv(DATA_DIR / "classical.csv")
df_pqc = pd.read_csv(DATA_DIR / "pqc.csv")

print("Classical data:")
print(df_classical)
print("\nPQC data:")
print(df_pqc)
print()

# Combine for some plots
df = pd.concat([df_classical, df_pqc], ignore_index=True)


def bar_plot(df_subset, title, filename):
    """Make a bar chart only if there is data."""
    if df_subset.empty:
        print(f"[SKIP] {title}: no matching rows")
        return

    plt.figure()
    grouped = df_subset.groupby(["algorithm", "operation"])["avg_time_s"].mean()
    grouped.plot(kind="bar")
    plt.ylabel("Average time (seconds)")
    plt.title(title)
    plt.tight_layout()
    out_path = OUT_DIR / filename
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Saved plot: {out_path}")


# 1. All keygen times (classical + PQC)
keygen_all = df[df["operation"] == "keygen"]
bar_plot(keygen_all, "Keygen Times (All Algorithms)", "keygen_all.png")

# 2. KEM operations for the PQC KEM algorithm (encaps/decaps/keygen)
kem_rows = df_pqc[df_pqc["operation"].isin(["keygen", "encaps", "decaps"])]
if not kem_rows.empty:
    kem_alg = kem_rows["algorithm"].unique()[0]
    kem_subset = kem_rows[kem_rows["algorithm"] == kem_alg]
    bar_plot(kem_subset, f"{kem_alg} KEM Operations", "kem_ops.png")
else:
    print("[SKIP] No KEM rows (keygen/encaps/decaps) found in pqc.csv")

# 3. Signature operations for the PQC signature algorithm (sign/verify/keygen)
sig_rows = df_pqc[df_pqc["operation"].isin(["keygen", "sign", "verify"])]
if not sig_rows.empty:
    sig_alg = sig_rows[sig_rows["operation"] == "sign"]["algorithm"].unique()[0]
    sig_subset = sig_rows[sig_rows["algorithm"] == sig_alg]
    bar_plot(sig_subset, f"{sig_alg} Signature Operations", "sig_ops.png")
else:
    print("[SKIP] No signature rows (keygen/sign/verify) found in pqc.csv")

print("\nDone.")

