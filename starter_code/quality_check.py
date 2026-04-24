# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

_TOXIC_KEYWORDS = [
    'null pointer exception',
    'traceback',
    'segmentation fault',
    'access denied',
    'stack overflow',
    'unhandled exception',
]


def run_quality_gate(document_dict) -> bool:
    doc_id = document_dict.get('document_id', '?')
    content = document_dict.get('content', '')

    # 1. Reject documents with content shorter than 20 characters
    if len(content.strip()) < 20:
        print(f"[QA] REJECT {doc_id}: content too short ({len(content)} chars).")
        return False

    # 2. Reject documents containing toxic / error strings
    content_lower = content.lower()
    for kw in _TOXIC_KEYWORDS:
        if kw in content_lower:
            print(f"[QA] REJECT {doc_id}: toxic string detected ('{kw}').")
            return False

    # 3. Flag logic discrepancy in legacy code
    #    process_legacy_code sets tax_discrepancy_detected in source_metadata
    meta = document_dict.get('source_metadata', {})
    if meta.get('tax_discrepancy_detected'):
        print(
            f"[QA] WARNING {doc_id}: tax rate discrepancy detected "
            f"(comment vs actual code). Allowing with flag."
        )
        # Warn but do not reject — the document is still valuable as a knowledge record

    return True
