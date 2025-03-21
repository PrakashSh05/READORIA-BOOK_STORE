from hashlib import pbkdf2_hmac
import binascii

# Given details
password = b"123456789"
salt = b"GF7pXgJdwu2KZH6H"
iterations = 260000
expected_hash = "cd326798046ca3b90b02bbbe8f970887d0f3148b7237ae103c6a0554a50d949a"

# Compute PBKDF2-HMAC-SHA256 hash
computed_hash = pbkdf2_hmac('sha256', password, salt, iterations)
computed_hash_hex = binascii.hexlify(computed_hash).decode()

# Compare hashes
print("Match:", computed_hash_hex == expected_hash)
