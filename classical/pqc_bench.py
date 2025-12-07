import time
import csv
from pathlib import Path

import oqs  # liboqs-python


DATA_DIR = Path.home() / "pq-project" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def choose_algorithms():
    """
    Pick reasonable defaults for KEM and signature algorithms.
    Tries to pick Kyber / ML-DSA if available, otherwise falls back
    to the first enabled algorithm in each list.
    """
    kems = oqs.get_enabled_kem_mechanisms()
    sigs = oqs.get_enabled_sig_mechanisms()

    print("Enabled KEM algorithms:")
    for name in kems:
        print("  ", name)

    print("\nEnabled signature algorithms:")
    for name in sigs:
        print("  ", name)

    # --- Choose KEM algorithm (Kyber / ML-KEM if possible) ---
    preferred_kem_names = ["Kyber768", "ML-KEM-768", "Kyber512", "ML-KEM-512"]
    kem_alg = None
    for cand in preferred_kem_names:
        if cand in kems:
            kem_alg = cand
            break
    if kem_alg is None:
        kem_alg = kems[0]
        print(f"\n[INFO] No preferred Kyber name found; using first KEM: {kem_alg}")
    else:
        print(f"\n[INFO] Using KEM algorithm: {kem_alg}")

    # --- Choose SIG algorithm (ML-DSA / Dilithium-like if possible) ---
    preferred_sig_names = ["ML-DSA-87", "ML-DSA-65", "ML-DSA-44", "Dilithium3", "Dilithium2"]
    sig_alg = None
    for cand in preferred_sig_names:
        if cand in sigs:
            sig_alg = cand
            break
    if sig_alg is None:
        sig_alg = sigs[0]
        print(f"[INFO] No preferred Dilithium/ML-DSA name found; using first SIG: {sig_alg}")
    else:
        print(f"[INFO] Using signature algorithm: {sig_alg}")

    print()  # blank line
    return kem_alg, sig_alg


def time_kem(alg_name, iterations=50):
    """
    Time KEM keygen, encaps, and decaps operations for a given algorithm.
    Uses the API: generate_keypair() -> pk, encap_secret(pk), decap_secret(ct).
    """
    with oqs.KeyEncapsulation(alg_name) as kem:
        # --- Keygen timing ---
        t0 = time.perf_counter()
        for _ in range(iterations):
            kem.generate_keypair()
        t1 = time.perf_counter()
        keygen_avg = (t1 - t0) / iterations

        # --- Encaps/decaps timing ---
        t_enc = []
        t_dec = []
        for _ in range(iterations):
            pk = kem.generate_keypair()
            t2 = time.perf_counter()
            ct, ss = kem.encap_secret(pk)  # public key passed here
            t3 = time.perf_counter()
            kem.decap_secret(ct)
            t4 = time.perf_counter()
            t_enc.append(t3 - t2)
            t_dec.append(t4 - t3)

        enc_avg = sum(t_enc) / iterations
        dec_avg = sum(t_dec) / iterations

    return keygen_avg, enc_avg, dec_avg


def time_sig(alg_name, iterations=50):
    """
    Time signature keygen, sign, and verify for a given algorithm.

    IMPORTANT: In your liboqs-python version, the API is:

        pk = sig.generate_keypair()      # returns ONE value (public key)
        signature = sig.sign(message)    # uses internal secret key
        sig.verify(message, signature, pk)

    So we do NOT unpack (pk, sk), and we do NOT pass sk into sign().
    """
    with oqs.Signature(alg_name) as sig:
        # --- Keygen timing ---
        t0 = time.perf_counter()
        for _ in range(iterations):
            sig.generate_keypair()
        t1 = time.perf_counter()
        keygen_avg = (t1 - t0) / iterations

        # Use one keypair for sign/verify timing
        pk = sig.generate_keypair()
        message = b"test message for signing"

        # --- Sign timing ---
        t_sign = []
        for _ in range(iterations):
            t2 = time.perf_counter()
            signature = sig.sign(message)      # no sk argument
            t3 = time.perf_counter()
            t_sign.append(t3 - t2)

        # --- Verify timing ---
        t_verify = []
        for _ in range(iterations):
            signature = sig.sign(message)
            t4 = time.perf_counter()
            sig.verify(message, signature, pk)
            t5 = time.perf_counter()
            t_verify.append(t5 - t4)

        sign_avg = sum(t_sign) / iterations
        verify_avg = sum(t_verify) / iterations

    return keygen_avg, sign_avg, verify_avg


def main():
    kem_alg, sig_alg = choose_algorithms()

    rows = []

    print(f"[*] Benchmarking KEM: {kem_alg}")
    kem_kg, kem_enc, kem_dec = time_kem(kem_alg)
    rows.extend([
        {"family": "pqc", "algorithm": kem_alg, "operation": "keygen", "avg_time_s": kem_kg},
        {"family": "pqc", "algorithm": kem_alg, "operation": "encaps", "avg_time_s": kem_enc},
        {"family": "pqc", "algorithm": kem_alg, "operation": "decaps", "avg_time_s": kem_dec},
    ])
    print(f"    keygen avg: {kem_kg:.6f} s")
    print(f"    encaps avg: {kem_enc:.6f} s")
    print(f"    decaps avg: {kem_dec:.6f} s\n")

    print(f"[*] Benchmarking Signature: {sig_alg}")
    sig_kg, sig_sign, sig_verify = time_sig(sig_alg)
    rows.extend([
        {"family": "pqc", "algorithm": sig_alg, "operation": "keygen", "avg_time_s": sig_kg},
        {"family": "pqc", "algorithm": sig_alg, "operation": "sign", "avg_time_s": sig_sign},
        {"family": "pqc", "algorithm": sig_alg, "operation": "verify", "avg_time_s": sig_verify},
    ])
    print(f"    keygen avg: {sig_kg:.6f} s")
    print(f"    sign avg: {sig_sign:.6f} s")
    print(f"    verify avg: {sig_verify:.6f} s\n")

    out_file = DATA_DIR / "pqc.csv"
    with out_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Saved {len(rows)} rows to {out_file}")


if __name__ == "__main__":
    main()

