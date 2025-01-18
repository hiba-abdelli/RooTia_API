import secrets

def generate_secret_key():
    return secrets.token_hex(32)

def generate_jwt_secret_key():
    return secrets.token_hex(32)

if __name__ == '__main__':
    secret_key = generate_secret_key()
    jwt_secret_key = generate_jwt_secret_key()
    print(f"Generated SECRET_KEY: {secret_key}")
    print(f"Generated JWT_SECRET_KEY: {jwt_secret_key}")
