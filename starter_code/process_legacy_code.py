import ast
import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.


def _detect_tax_discrepancy(source_code: str) -> str | None:
    """
    legacy_tax_calc has no docstring — only inline comments.
    Extract the comment block for that function and compare the actual
    tax_rate value with any percentage mentioned in the comments.
    Returns a discrepancy description, or None.
    """
    # Isolate the legacy_tax_calc function body
    func_start = source_code.find('def legacy_tax_calc')
    if func_start == -1:
        return None

    func_body = source_code[func_start:]

    # Collect all comment lines inside this function
    comment_lines = re.findall(r'#\s*(.*)', func_body)
    comment_text = ' '.join(comment_lines)

    # Extract all percentages mentioned in comments
    comment_pcts = re.findall(r'(\d+)%', comment_text)

    # Extract the actual tax_rate value
    rate_match = re.search(r'tax_rate\s*=\s*([\d.]+)', func_body)
    if not rate_match:
        return None

    actual_rate = float(rate_match.group(1))
    actual_pct_int = int(round(actual_rate * 100))

    # Flag if any percentage in the comments differs from the actual code
    for claimed in comment_pcts:
        if int(claimed) != actual_pct_int:
            return (
                f"TAX DISCREPANCY DETECTED in legacy_tax_calc: "
                f"comment references {claimed}% but code executes {actual_pct_int}%."
            )

    return None


def extract_logic_from_code(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    # ------------------------------------------

    # Use ast to find docstrings
    tree = ast.parse(source_code)
    docstrings = []

    module_doc = ast.get_docstring(tree)
    if module_doc:
        docstrings.append(f"Module: {module_doc}")

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

    # Detect tax discrepancy (legacy_tax_calc has no docstring, only comments)
    discrepancy = _detect_tax_discrepancy(source_code)
    if discrepancy:
        content += f"\n\n{discrepancy}"

    return {
        "document_id": "code-legacy-001",
        "content": content,
        "source_type": "Code",
        "creator": "Senior Dev (retired)",
        "created_at": None,
        "source_metadata": {
            "original_file": "legacy_pipeline.py",
            "has_tax_logic": "legacy_tax_calc" in source_code,
            "tax_discrepancy_detected": discrepancy is not None,
        },
    }
