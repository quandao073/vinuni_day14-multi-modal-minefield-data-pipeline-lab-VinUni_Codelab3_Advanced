import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# ROLE 2 (assigned to Người 1): ETL — PDF
# ==========================================
# Task: Extract structured metadata from lecture_notes.pdf via Gemini API.
# Must implement exponential backoff for 429 (rate-limit) errors.

MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 2  # doubles each retry: 2 → 4 → 8 → 16 → 32


def _call_gemini_with_backoff(model_name, contents, *, max_retries=MAX_RETRIES):
    """
    Call Gemini's generate_content with exponential backoff on 429 errors.
    Raises on non-retryable errors immediately.
    """
    backoff = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
            )
            return response
        except Exception as e:
            error_str = str(e)
            # Retry only on rate-limit (429) errors
            if "429" in error_str or "Resource has been exhausted" in error_str:
                if attempt == max_retries:
                    print(f"[PDF] Max retries ({max_retries}) exhausted. Giving up.")
                    raise
                print(
                    f"[PDF] Rate-limited (attempt {attempt}/{max_retries}). "
                    f"Retrying in {backoff}s …"
                )
                time.sleep(backoff)
                backoff *= 2  # exponential backoff
            else:
                # Non-retryable error — fail fast
                raise


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences that Gemini sometimes wraps around JSON."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):]
    elif text.startswith("```"):
        text = text[len("```"):]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def extract_pdf_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    # --- Upload ---
    print(f"Uploading {file_path} to Gemini...")
    try:
        pdf_file = client.files.upload(file=file_path)
    except Exception as e:
        print(f"Failed to upload file to Gemini: {e}")
        return None

    prompt = """
Analyze this document and extract a summary and the author. 
Output exactly as a JSON object matching this exact format:
{
    "document_id": "pdf-doc-001",
    "content": "Summary: [Insert your 3-sentence summary here]",
    "source_type": "PDF",
    "author": "[Insert author name here]",
    "timestamp": null,
    "source_metadata": {"original_file": "lecture_notes.pdf"}
}
"""

    # --- Generate with backoff ---
    print("Generating content from PDF using Gemini...")
    try:
        response = _call_gemini_with_backoff(
            "gemini-2.5-flash",
            [pdf_file, prompt],
        )
    except Exception as e:
        print(f"[PDF] Gemini generation failed: {e}")
        return None

    content_text = _clean_json_response(response.text)

    try:
        extracted_data = json.loads(content_text)
    except json.JSONDecodeError as e:
        print(f"[PDF] Failed to parse Gemini response as JSON: {e}")
        print(f"[PDF] Raw response:\n{content_text[:500]}")
        return None

    return extracted_data
