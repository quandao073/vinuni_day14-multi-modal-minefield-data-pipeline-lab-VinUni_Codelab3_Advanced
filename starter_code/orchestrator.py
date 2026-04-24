import json
import time
import os

# Robust path handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "raw_data")


# Import role-specific modules
from schema import UnifiedDocument
from process_pdf import extract_pdf_data
from process_transcript import clean_transcript
from process_html import parse_html_catalog
from process_csv import process_sales_csv
from process_legacy_code import extract_logic_from_code
from quality_check import run_quality_gate

# ==========================================
# ROLE 4: DEVOPS & INTEGRATION SPECIALIST
# ==========================================
# Task: Orchestrate the ingestion pipeline and handle errors/SLA.

def _validate_and_add(doc_dict, label: str, final_kb: list):
    """Validate a processor output against UnifiedDocument schema, then quality-gate it."""
    if not doc_dict:
        return
    try:
        validated = UnifiedDocument(**doc_dict)
    except Exception as e:
        print(f"[{label}] SCHEMA ERROR — skipping: {e}")
        return
    if run_quality_gate(doc_dict):
        final_kb.append(validated.model_dump(mode="json"))


def main():
    start_time = time.time()
    final_kb = []

    # --- FILE PATH SETUP (Handled for students) ---
    pdf_path   = os.path.join(RAW_DATA_DIR, "lecture_notes.pdf")
    trans_path = os.path.join(RAW_DATA_DIR, "demo_transcript.txt")
    html_path  = os.path.join(RAW_DATA_DIR, "product_catalog.html")
    csv_path   = os.path.join(RAW_DATA_DIR, "sales_records.csv")
    code_path  = os.path.join(RAW_DATA_DIR, "legacy_pipeline.py")
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "processed_knowledge_base.json")
    # ----------------------------------------------

    print("Starting Multi-Modal Ingestion Pipeline...")

    # 1. PDF
    t0 = time.time()
    print("[PDF] Processing...")
    _validate_and_add(extract_pdf_data(pdf_path), "PDF", final_kb)
    print(f"[PDF] Done in {time.time()-t0:.2f}s")

    # 2. Transcript
    t0 = time.time()
    print("[Transcript] Processing...")
    _validate_and_add(clean_transcript(trans_path), "Transcript", final_kb)
    print(f"[Transcript] Done in {time.time()-t0:.2f}s")

    # 3. HTML
    t0 = time.time()
    print("[HTML] Processing...")
    for doc in parse_html_catalog(html_path):
        _validate_and_add(doc, "HTML", final_kb)
    print(f"[HTML] Done in {time.time()-t0:.2f}s")

    # 4. CSV
    t0 = time.time()
    print("[CSV] Processing...")
    for doc in process_sales_csv(csv_path):
        _validate_and_add(doc, "CSV", final_kb)
    print(f"[CSV] Done in {time.time()-t0:.2f}s")

    # 5. Legacy Code
    t0 = time.time()
    print("[Code] Processing...")
    _validate_and_add(extract_logic_from_code(code_path), "Code", final_kb)
    print(f"[Code] Done in {time.time()-t0:.2f}s")

    # --- SAVE OUTPUT ---
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_kb, f, indent=4, ensure_ascii=False)

    end_time = time.time()
    print(f"\nKnowledge Base saved to {output_path}")
    print(f"Pipeline finished in {end_time - start_time:.2f} seconds.")
    print(f"Total valid documents stored: {len(final_kb)}")


if __name__ == "__main__":
    main()
