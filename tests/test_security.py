from api.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    password = "test-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(
        password,
        hashed_password,
    )
    assert not verify_password(
        "wrong-password",
        hashed_password,
    )


def test_create_and_decode_access_token():
    token = create_access_token(user_id=1)

    user_id = decode_access_token(token)

    assert user_id == 1