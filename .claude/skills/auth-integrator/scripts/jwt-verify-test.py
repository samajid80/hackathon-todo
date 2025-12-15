#!/usr/bin/env python3

import sys
from jose import jwt, JWTError  # Assuming jose is added to deps

def verify_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        print("Decoded Payload:", payload)
        return payload
    except JWTError as e:
        print("Error:", str(e))
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: jwt-verify-test.py <token> <secret>")
        sys.exit(1)
    
    token = sys.argv[1]
    secret = sys.argv[2]
    verify_token(token, secret)