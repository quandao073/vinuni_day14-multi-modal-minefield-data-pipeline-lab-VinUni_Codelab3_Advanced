# The Multi-Modal Minefield — Data Pipeline Lab
**VinUni AI Lab · Codelab 03 Advanced**

---

## Giới thiệu

Bài lab xây dựng một **data ingestion pipeline** đa nguồn cho Knowledge Base (KB). Pipeline thu nạp và chuẩn hóa dữ liệu từ 5 định dạng khác nhau (PDF, CSV, HTML, Transcript, Legacy Python Code), áp dụng quality gate ngữ nghĩa, và xuất ra một file JSON hợp nhất.

**Thách thức chính:**
- Dữ liệu "nhiễm độc": giá tiền nhiều định dạng, timestamp không nhất quán, noise token trong transcript
- Mid-Lab Incident: schema breaking change (v1 → v2) tại phút 60
- Forensic agent kiểm tra chất lượng data sau khi nộp

---

## Cấu trúc dự án

```
├── raw_data/                   # Dữ liệu gốc (không chỉnh sửa)
│   ├── lecture_notes.pdf
│   ├── sales_records.csv
│   ├── product_catalog.html
│   ├── demo_transcript.txt
│   └── legacy_pipeline.py
├── starter_code/               # Code chính của nhóm
│   ├── schema.py               # UnifiedDocument v2 (Pydantic)
│   ├── process_pdf.py          # ETL: Gemini API + exponential backoff
│   ├── process_html.py         # ETL: BeautifulSoup catalog parser
│   ├── process_csv.py          # ETL: pandas, dedup, price/date cleaning
│   ├── process_transcript.py   # ETL: regex noise removal, Vietnamese NLP
│   ├── process_legacy_code.py  # ETL: AST docstring extraction, discrepancy detection
│   ├── quality_check.py        # Semantic quality gates
│   └── orchestrator.py         # DAG pipeline, SLA tracking, JSON output
├── forensic_agent/
│   └── agent_forensic.py       # Kiểm tra tự động kết quả
├── processed_knowledge_base.json  # Output (28 documents)
├── PLAN.md                     # Kế hoạch phân công nhóm
└── README.md
```

---

## Thành viên nhóm & Đóng góp

### Nguyễn Duy Minh Hoàng — `hirin`
**Mã SV:** 2A202600155 · **Email:** nguyenduyminhhoang@gmail.com
**Vai trò:** Lead Data Architect + ETL PDF & HTML (Người 1)

| Commit | Mô tả |
|--------|-------|
| `096c213` | `feat(schema)`: Định nghĩa `UnifiedDocument` v1 bằng Pydantic — đầy đủ validators (reject empty content, invalid source_type), thêm `schema_version` chuẩn bị migration |
| `0e616bd` | `feat(pdf)`: Implement Gemini extraction + exponential backoff (2→4→8→16→32s, max 5 retries) cho lỗi 429; migrate sang `google-genai` SDK mới |
| `07e313e` | `feat(html)`: BeautifulSoup catalog parser — tìm `#main-catalog`, bỏ nav/sidebar/footer boilerplate, xử lý giá `N/A`/`Liên hệ` → `None`, chuẩn hóa VND |
| `a2da732` | `chore`: Bảo vệ `.env` (API key) khỏi bị commit nhầm |
| `24e5177` | `chore`: Thêm `__pycache__` vào `.gitignore` |

---

### Nguyễn Đôn Đức — `edward1503`
**Mã SV:** 2A202600145 · **Email:** nguyendonduc1503@gmail.com
**Vai trò:** Schema Migration Lead + Integration (Người 3 — giai đoạn Mid-Lab Incident)

| Commit | Mô tả |
|--------|-------|
| `c5e8138` | `update task 3`: Thực hiện **schema v2 migration** toàn pipeline — đổi `author` → `creator`, `timestamp` → `created_at` trên cả 9 files; implement `process_legacy_code.py` (AST extraction), `quality_check.py` (toxic gate, discrepancy flag), hoàn thiện `orchestrator.py` (DAG đầy đủ, JSON output) |

---

### Đào Anh Quân — `quandao073`
**Mã SV:** 2A202600028 · **Email:** anhquan7303qqq@gmail.com
**Vai trò:** ETL CSV & Transcript + QA/Orchestrator Enhancement (Người 2 + review)

| Commit | Mô tả |
|--------|-------|
| `ba7754b` | `PLAN.md`: Lập kế hoạch phân công nhóm 3 người, ước tính thời gian, quy tắc phối hợp |
| `2dd8884` | `feat`: Implement `process_csv.py` — dedup theo `id`, clean 6 kiểu price trap (`$1200`, `N/A`, `five dollars`, `-350000`, `Liên hệ`, `NULL`), chuẩn hóa 8 định dạng ngày; implement `process_transcript.py` — loại timestamp/noise, parse giá tiếng Việt "năm trăm nghìn" → 500,000 |
| `98ee4e4` | `feat`: Refactor `process_legacy_code.py` — thêm `_detect_tax_discrepancy()` phát hiện sai lệch comment 8% vs code 10%; nâng cấp `quality_check.py` — dùng `source_metadata` flag thay vì text matching; nâng cấp `orchestrator.py` — thêm `_validate_and_add()` validate `UnifiedDocument` trước khi append, đo SLA từng bước |

---

## Kết quả

Pipeline xử lý thành công **28 documents** từ 5 nguồn:

| Nguồn | File | Documents |
|-------|------|-----------|
| PDF | `lecture_notes.pdf` | 1 |
| Transcript | `demo_transcript.txt` | 1 |
| HTML | `product_catalog.html` | 5 |
| CSV | `sales_records.csv` | 20 (sau dedup từ 21 rows) |
| Legacy Code | `legacy_pipeline.py` | 1 |
| **Tổng** | | **28** |

---

## Cài đặt & Chạy

```bash
# 1. Cài thư viện
pip install -r requirements.txt

# 2. Tạo .env với Gemini API Key
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. Thêm lecture_notes.pdf vào raw_data/

# 4. Chạy pipeline
cd starter_code
python orchestrator.py

# 5. Kiểm tra kết quả
python ../forensic_agent/agent_forensic.py
```

Output: `processed_knowledge_base.json` ở thư mục gốc.

---

## Các vấn đề kỹ thuật đáng chú ý

- **Gemini 429 retry**: Exponential backoff 2s → 32s, không retry lỗi non-rate-limit
- **Tax discrepancy**: `legacy_tax_calc` có comment nói "8%" nhưng code thực thi 10% — phát hiện bằng AST + regex comment scan, không phải text matching
- **Schema migration**: `author`/`timestamp` (v1) → `creator`/`created_at` (v2); `schema_version` field giúp trace migration
- **Negative stock**: SP-004 có `stock=-5` → `None` (reject tại HTML processor, không để lọt vào KB)
