#!/usr/bin/env python3

import sys
import re

def validate_schema(code: str) -> str:
    """Validate SQLModel schema code for best practices."""
    issues = []
    
    # Check for primary key
    if not re.search(r'id:\s*(int|Integer)\s*,\s*primary_key=True', code):
        issues.append("Missing primary key 'id' in model.")
    
    # Check for indexes
    if 'completed' in code and not re.search(r'Index\("ix_tasks_completed"\)', code):
        issues.append("Missing index on 'completed' field.")
    
    # Check for foreign key
    if 'user_id' in code and not re.search(r'ForeignKey\("users.id"\)', code):
        issues.append("Missing foreign key on 'user_id'.")
    
    if issues:
        return "Validation Issues:\n" + "\n".join(issues)
    return "Schema valid: No issues found."

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: schema-validator.py '<code_snippet>'")
        sys.exit(1)
    
    code_snippet = sys.argv[1]
    result = validate_schema(code_snippet)
    print(result)