from app.core.security import hash_password, verify_password
h = hash_password("admin1234")
print("Hash:", h)
print("Verify:", verify_password("admin1234", h))
