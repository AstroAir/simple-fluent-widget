#!/usr/bin/env python3
"""
Syntax test for rich_text.py
"""
import ast
import sys

def check_syntax(filename):
    """Check Python syntax of a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the AST
        ast.parse(content)
        print(f"✅ {filename} has valid Python syntax")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}")
        print(f"   Error: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return False

if __name__ == "__main__":
    filename = "components/data/rich_text.py"
    if check_syntax(filename):
        sys.exit(0)
    else:
        sys.exit(1)
