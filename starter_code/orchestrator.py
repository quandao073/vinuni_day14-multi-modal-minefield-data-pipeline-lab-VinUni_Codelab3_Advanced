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

def main():
    start_time = time.time()
    final_kb = []
    
    # --- FILE PATH SETUP (Handled for students) ---
    pdf_path = os.path.join(RAW_DATA_DIR, "lecture_notes.pdf")
    trans_path = os.path.join(RAW_DATA_DIR, "demo_transcript.txt")
    html_path = os.path.join(RAW_DATA_DIR, "product_catalog.html")
    csv_path = os.path.join(RAW_DATA_DIR, "sales_records.csv")
    code_path = os.path.join(RAW_DATA_DIR, "legacy_pipeline.py")
    
    output_path = os.path.join(os.path.dirname(SCRIPT_DIR), "processed_knowledge_base.json")
    # ----------------------------------------------

    # --- ETL EXECUTION ---
    print("Starting Multi-Modal Ingestion Pipeline...")
    
    # 1. PDF
    print("[PDF] Processing...")
    pdf_doc = extract_pdf_data(pdf_path)
    if pdf_doc and run_quality_gate(pdf_doc):
        final_kb.append(pdf_doc)
        
    # 2. Transcript
    print("[Transcript] Processing...")
    trans_doc = clean_transcript(trans_path)
    if trans_doc and run_quality_gate(trans_doc):
        final_kb.append(trans_doc)
        
    # 3. HTML
    print("[HTML] Processing...")
    html_docs = parse_html_catalog(html_path)
    for doc in html_docs:
        if doc and run_quality_gate(doc):
            final_kb.append(doc)
            
    # 4. CSV
    print("[CSV] Processing...")
    csv_docs = process_sales_csv(csv_path)
    for doc in csv_docs:
        if doc and run_quality_gate(doc):
            final_kb.append(doc)
            
    # 5. Legacy Code
    print("[Code] Processing...")
    code_doc = extract_logic_from_code(code_path)
    if code_doc and run_quality_gate(code_doc):
        final_kb.append(code_doc)

    # --- SAVE OUTPUT ---
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(final_kb, f, indent=4, ensure_ascii=False)
    
    print(f"Knowledge Base saved to {output_path}")

    end_time = time.time()
    print(f"Pipeline finished in {end_time - start_time:.2f} seconds.")
    print(f"Total valid documents stored: {len(final_kb)}")


if __name__ == "__main__":
    main()
