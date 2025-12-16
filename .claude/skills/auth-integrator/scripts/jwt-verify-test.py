#!/usr/bin/env python3
"""
JWT Verification Test Script

This script tests JWT token generation and verification to ensure
the authentication setup is working correctly.

Usage:
    python jwt-verify-test.py [--secret SECRET] [--user-id USER_ID]
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional

try:
    from jose import jwt, JWTError
except ImportError:
    print("Error: python-jose is not installed")
    print("Install with: pip install python-jose[cryptography]")
    sys.exit(1)


def generate_test_token(
    user_id: str = "test-user-123",
    secret: Optional[str] = None,
    expires_minutes: int = 60
) -> str:
    """Generate a test JWT token"""
    if secret is None:
        secret = os.getenv("BETTER_AUTH_SECRET")
    
    if not secret:
        raise ValueError(
            "No secret provided. Set BETTER_AUTH_SECRET environment variable "
            "or pass --secret parameter"
        )
    
    # Create token payload
    payload = {
        "sub": user_id,
        "email": f"{user_id}@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "iat": datetime.utcnow(),
    }
    
    # Generate token
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def verify_test_token(token: str, secret: Optional[str] = None) -> dict:
    """Verify a JWT token and return the payload"""
    if secret is None:
        secret = os.getenv("BETTER_AUTH_SECRET")
    
    if not secret:
        raise ValueError(
            "No secret provided. Set BETTER_AUTH_SECRET environment variable "
            "or pass --secret parameter"
        )
    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except JWTError as e:
        raise ValueError(f"Token verification failed: {str(e)}")


def run_tests(secret: Optional[str] = None, user_id: str = "test-user-123"):
    """Run a series of JWT verification tests"""
    print("=" * 60)
    print("JWT Verification Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Generate valid token
    print("Test 1: Generate valid token")
    try:
        token = generate_test_token(user_id, secret)
        print(f"✓ Token generated successfully")
        print(f"  Token: {token[:50]}...")
        print()
    except Exception as e:
        print(f"✗ Failed to generate token: {e}")
        return False
    
    # Test 2: Verify valid token
    print("Test 2: Verify valid token")
    try:
        payload = verify_test_token(token, secret)
        print(f"✓ Token verified successfully")
        print(f"  User ID: {payload.get('sub')}")
        print(f"  Email: {payload.get('email')}")
        print(f"  Issued at: {datetime.fromtimestamp(payload.get('iat'))}")
        print(f"  Expires at: {datetime.fromtimestamp(payload.get('exp'))}")
        print()
    except Exception as e:
        print(f"✗ Failed to verify token: {e}")
        return False
    
    # Test 3: Verify with wrong secret
    print("Test 3: Verify with wrong secret (should fail)")
    try:
        wrong_secret = "wrong-secret-key-12345678901234567890"
        verify_test_token(token, wrong_secret)
        print(f"✗ Token verified with wrong secret (this should not happen!)")
        return False
    except Exception as e:
        print(f"✓ Correctly rejected token with wrong secret")
        print(f"  Error: {e}")
        print()
    
    # Test 4: Verify expired token
    print("Test 4: Verify expired token (should fail)")
    try:
        expired_token = generate_test_token(user_id, secret, expires_minutes=-10)
        verify_test_token(expired_token, secret)
        print(f"✗ Expired token verified (this should not happen!)")
        return False
    except Exception as e:
        print(f"✓ Correctly rejected expired token")
        print(f"  Error: {e}")
        print()
    
    # Test 5: Manual token decoding (without verification)
    print("Test 5: Manual token inspection")
    try:
        # Decode without verification to inspect payload
        unverified = jwt.get_unverified_claims(token)
        print(f"✓ Token payload (unverified):")
        for key, value in unverified.items():
            if key in ['exp', 'iat']:
                value = f"{value} ({datetime.fromtimestamp(value)})"
            print(f"  {key}: {value}")
        print()
    except Exception as e:
        print(f"✗ Failed to decode token: {e}")
        return False
    
    print("=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test JWT token generation and verification"
    )
    parser.add_argument(
        "--secret",
        help="Secret key for JWT signing (or set BETTER_AUTH_SECRET env var)",
        default=None
    )
    parser.add_argument(
        "--user-id",
        help="User ID to use in test token",
        default="test-user-123"
    )
    parser.add_argument(
        "--token",
        help="Existing token to verify (skips generation)",
        default=None
    )
    
    args = parser.parse_args()
    
    # If secret not provided, check environment
    secret = args.secret or os.getenv("BETTER_AUTH_SECRET")
    
    if not secret:
        print("Error: No secret key provided")
        print()
        print("Either:")
        print("  1. Set BETTER_AUTH_SECRET environment variable")
        print("  2. Pass --secret parameter")
        print()
        print("Example:")
        print("  export BETTER_AUTH_SECRET='your-secret-key'")
        print("  python jwt-verify-test.py")
        print()
        print("Or:")
        print("  python jwt-verify-test.py --secret 'your-secret-key'")
        sys.exit(1)
    
    # Check secret length
    if len(secret) < 32:
        print("Warning: Secret key is shorter than 32 characters")
        print("For production, use at least 32 characters")
        print()
    
    # If token provided, just verify it
    if args.token:
        print(f"Verifying provided token...")
        print()
        try:
            payload = verify_test_token(args.token, secret)
            print(f"✓ Token is valid!")
            print()
            print("Payload:")
            for key, value in payload.items():
                if key in ['exp', 'iat']:
                    value = f"{value} ({datetime.fromtimestamp(value)})"
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"✗ Token verification failed: {e}")
            sys.exit(1)
    else:
        # Run full test suite
        success = run_tests(secret, args.user_id)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
