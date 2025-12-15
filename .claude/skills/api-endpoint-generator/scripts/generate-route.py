#!/usr/bin/env python3

import sys

def generate_route(method: str, endpoint: str, has_auth: bool = True) -> str:
    """Generate basic FastAPI route code from inputs."""
    auth_dep = ", depends=[get_current_user]" if has_auth else ""
    body = "pass  # Add SQLModel logic here"
    
    if method.upper() == "POST":
        body = "db.add(new_item); db.commit(); return new_item"
    
    template = f"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
# Import models, db session, get_current_user

router = APIRouter(prefix="/api")

@router.{method.lower()}("{endpoint}"{auth_dep})
async def {method.lower()}_{endpoint.strip('/').replace('/', '_')}(current_user = Depends(get_current_user)):
    {body}
"""
    return template

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate-route.py <method> <endpoint> [has_auth]")
        sys.exit(1)
    
    method = sys.argv[1]
    endpoint = sys.argv[2]
    has_auth = len(sys.argv) > 3 and sys.argv[3].lower() == 'true'
    
    output = generate_route(method, endpoint, has_auth)
    print(output)