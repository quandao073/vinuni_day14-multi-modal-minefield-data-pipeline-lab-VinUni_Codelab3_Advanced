import ast

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.

import re

def extract_logic_from_code(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    # ------------------------------------------
    
    # Use ast to find docstrings
    tree = ast.parse(source_code)
    docstrings = []
    
    # Module level docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        docstrings.append(f"Module: {module_doc}")
    
    # Function level docstrings
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            if doc:
                docstrings.append(f"Function '{node.name}': {doc.strip()}")

    # Find Business Logic Rules in comments
    rules = re.findall(r'#\s*(Business Logic Rule \d+:.*)', source_code, re.IGNORECASE)
    
    content = "\n".join(docstrings)
    if rules:
        content += "\n\nExtracted Rules:\n" + "\n".join(rules)

    return {
        "document_id": "code-legacy-001",
        "content": content,
        "source_type": "Code",
        "creator": "Senior Dev (retired)",
        "created_at": None,
        "source_metadata": {
            "original_file": "legacy_pipeline.py",
            "has_tax_logic": "legacy_tax_calc" in source_code
        }
    }

