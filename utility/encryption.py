import bcrypt


def hash_password(password: str):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def check_password(input_password: str, hashed_password_string: str) -> bool:
    return bcrypt.checkpw(
        input_password.encode("utf-8"), hashed_password_string.encode("utf-8")
    )
