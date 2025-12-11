#!/usr/bin/env python3

import sys
import re

def generate_tsx(component_name: str, description: str, is_client: bool = False) -> str:
    """Generate basic TSX component from description."""
    header = "'use client';\n" if is_client else ""
    props = "props: { [key: string]: any }"  # Simple placeholder; expand based on desc
    body = "return <div className='p-4 bg-white rounded shadow'>Component Content</div>;"  # Template fill
    
    # Basic parsing: Add form if 'form' in desc
    if 'form' in description.lower():
        body = """
return (
  <form onSubmit={handleSubmit} className="space-y-4">
    <input type="text" placeholder="Title" className="border p-2" />
    <textarea placeholder="Description" className="border p-2" />
    <button type="submit" className="bg-blue-500 text-white p-2">Submit</button>
  </form>
);
"""
    
    template = f"""
{header}
import React from 'react';

export default function {component_name}({{ {props} }}) {{
  {body}
}}
"""
    return template

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: tsx-generator.py <component_name> <description> [is_client]")
        sys.exit(1)
    
    name = sys.argv[1]
    desc = sys.argv[2]
    is_client = len(sys.argv) > 3 and sys.argv[3].lower() == 'true'
    
    output = generate_tsx(name, desc, is_client)
    print(output)