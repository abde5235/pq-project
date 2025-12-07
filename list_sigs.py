import oqs

print("Enabled signature algorithms:")
for name in oqs.get_enabled_sig_mechanisms():
    print("  ", name)
