import re

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================

# Vietnamese number words → numeric values
_VN_WORD_TO_NUM = {
    'một': 1, 'hai': 2, 'ba': 3, 'bốn': 4, 'năm': 5,
    'sáu': 6, 'bảy': 7, 'tám': 8, 'chín': 9, 'mười': 10,
    'trăm': 100, 'nghìn': 1_000, 'triệu': 1_000_000, 'tỷ': 1_000_000_000,
}

_VN_ALL_WORDS = '|'.join(_VN_WORD_TO_NUM.keys())
_VN_PRICE_RE = re.compile(
    rf'((?:{_VN_ALL_WORDS})(?:\s+(?:{_VN_ALL_WORDS})){{1,}})',
    re.IGNORECASE,
)


def _parse_vietnamese_number(text: str):
    """
    Convert a Vietnamese number phrase to an integer.
    Example: "năm trăm nghìn" → 500_000
    """
    words = text.lower().split()
    value = 0
    current = 0
    for w in words:
        n = _VN_WORD_TO_NUM.get(w)
        if n is None:
            continue
        if n >= 1_000:
            # e.g. nghìn, triệu — multiply accumulated current, add to value
            value += (current if current else 1) * n
            current = 0
        elif n >= 100:
            # e.g. trăm — multiply current digit
            current = (current if current else 1) * n
        else:
            current += n
    value += current
    return value if value > 0 else None


def clean_transcript(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # ------------------------------------------

    # Remove timestamps like [00:05:12]
    text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]\s*', '', text)

    # Remove noise tokens: [Music starts], [Music ends], [inaudible], [Laughter]
    # Keep [Speaker N] for now so we can extract the primary speaker
    text = re.sub(r'\[(?!Speaker)[^\]]+\]\s*', '', text)

    # Extract primary speaker (first speaker found)
    speaker_match = re.search(r'\[Speaker (\d+)\]', text)
    primary_speaker = f"Speaker {speaker_match.group(1)}" if speaker_match else "Unknown"

    # Remove speaker labels [Speaker N]:
    text = re.sub(r'\[Speaker \d+\]:\s*', '', text)

    # Collapse extra whitespace and blank lines
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text).strip()

    # Find Vietnamese price phrase
    vn_match = _VN_PRICE_RE.search(text)
    price_vnd = _parse_vietnamese_number(vn_match.group(1)) if vn_match else None

    return {
        "document_id": "transcript-001",
        "content": text,
        "source_type": "Video",
        "creator": primary_speaker,
        "created_at": None,
        "source_metadata": {
            "original_file": "demo_transcript.txt",
            "detected_price_vnd": price_vnd,
        },
    }
