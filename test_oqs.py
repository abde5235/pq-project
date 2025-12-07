import oqs

print("Enabled KEM algorithms:")
for name in oqs.get_enabled_kem_mechanisms():
    print("  ", name)

# Try a single KEM round with one algorithm (we'll adjust the name if needed)
alg_name = "Kyber768"  # if this fails, we'll switch to something from the list

print("\nTesting KEM with:", alg_name)

with oqs.KeyEncapsulation(alg_name) as kem:
    pk = kem.generate_keypair()
    ct, ss1 = kem.encap_secret(pk)
    ss2 = kem.decap_secret(ct)
    print("Shared secrets equal?", ss1 == ss2)
    print("Ciphertext length:", len(ct), "Secret length:", len(ss1))
