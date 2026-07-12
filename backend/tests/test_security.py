from app.core.security import hash_password, verify_password


def test_password_can_be_hashed_and_verified() -> None:
    password = "admin1234"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("senha-incorreta", password_hash)