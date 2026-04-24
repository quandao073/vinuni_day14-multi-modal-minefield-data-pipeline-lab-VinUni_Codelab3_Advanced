# Kế Hoạch Nhóm 3 Người — The Multi-Modal Minefield Lab

**Thời gian**: 10:00 – 13:00 (3 tiếng)  
**Thành viên**: 3 người  
**Mục tiêu**: Xây dựng data pipeline hoàn chỉnh, vượt qua forensic agent kiểm tra

---

## Phân Công Vai Trò (Đã cân bằng tải)

> Ước tính thời gian dựa trên phân tích starter code thực tế.  
> `process_pdf.py` đã có ~80% code → Người 1 nhẹ hơn → gánh thêm việc phối hợp schema.

| Người | File phụ trách | Ước tính |
|-------|---------------|----------|
| **Người 1** — Schema & Structured Data | `schema.py`, `process_pdf.py`, `process_html.py` | ~110 phút code + phối hợp schema migration |
| **Người 2** — Tabular & Text Data | `process_csv.py`, `process_transcript.py` | ~110 phút |
| **Người 3** — Code Analysis & Integration | `process_legacy_code.py`, `quality_check.py`, `orchestrator.py` | ~155 phút |

### Lý do phân chia này

- **Người 1** nhận `process_pdf.py` vì nó đã có sẵn ~80% code (Gemini API call, JSON parsing) — tiết kiệm ~30 phút để bù cho nhiệm vụ schema migration lúc 11:00.
- **Người 2** nhận hai file ETL thuần regex/pandas — khối lượng tương đương nhau, không phụ thuộc lẫn nhau, làm song song dễ dàng.
- **Người 3** nhận `process_legacy_code.py` vì nó liên quan trực tiếp đến `quality_check.py` (cần phát hiện discrepancy thuế 8% vs 10% trong `legacy_pipeline.py`). Sau đó tự nhiên chuyển sang `orchestrator.py`.

---

## Kế Hoạch Thời Gian Chi Tiết

### Giai đoạn 1 — Khởi động (10:00 – 10:20) — *cả nhóm*

- [ ] Cài đặt: `pip install -r requirements.txt`
- [ ] Tạo `.env` với `GEMINI_API_KEY`
- [ ] Thêm `lecture_notes.pdf` vào `raw_data/`
- [ ] Người 1 trình bày nhanh schema v1 để cả nhóm thống nhất trước khi tách ra làm

---

### Giai đoạn 2 — Phát triển song song (10:20 – 11:00)

**Người 1 — Schema + PDF + HTML:**
- [ ] Hoàn thiện `schema.py` v1 — đảm bảo các field: `document_id`, `content`, `source_type`, `author`, `timestamp`, `source_metadata`
- [ ] **Commit `schema.py` trước 10:40** để Người 2 và 3 có thể import
- [ ] Bắt đầu `process_pdf.py`: test Gemini API, thêm exponential backoff cho lỗi `429`
- [ ] Bắt đầu `process_html.py`: BeautifulSoup tìm `#main-catalog`, xử lý giá `N/A` / `Liên hệ`

**Người 2 — CSV + Transcript:**
- [ ] `process_csv.py`: xóa duplicate theo `id`, chuẩn hóa giá (`"$1200"` → `1200.0`, `"five dollars"` → bỏ), chuẩn ngày `YYYY-MM-DD`
- [ ] `process_transcript.py`: regex loại `[00:05:12]`, `[Music]`, `[inaudible]`; tìm giá bằng tiếng Việt (`"năm trăm nghìn"`)

**Người 3 — Legacy Code + QA skeleton:**
- [ ] `process_legacy_code.py`: dùng `ast` để extract docstring từ các hàm; dùng regex tìm `# Business Logic Rule \d+`; **đặc biệt: phát hiện `legacy_tax_calc` có comment nói 8% nhưng code thực chạy 10%**
- [ ] Bắt đầu `quality_check.py` skeleton: từ chối document có `content` < 20 ký tự

---

### Giai đoạn 3 — Mid-Lab Incident + Hoàn thiện (11:00 – 11:20)

> ⚠️ **CẢNH BÁO: Lúc 11:00 "khách hàng" công bố breaking change — Schema v2!**  
> Ví dụ: đổi tên field, thêm field bắt buộc. Toàn nhóm dừng lại 15 phút để xử lý.

**Người 1 — Schema migration (ưu tiên cao nhất):**
- [ ] Nhận thay đổi, cập nhật `schema.py` v2 ngay lập tức
- [ ] Thông báo qua chat nhóm: "Field X đổi thành Y, thêm field Z"
- [ ] Commit `schema.py` v2 ngay, không chờ

**Người 2 và 3 — Cập nhật theo schema v2:**
- [ ] Sửa tất cả `return {}` / `return []` để output đúng field tên mới
- [ ] Chạy nhanh từng hàm với file test để kiểm tra không bị lỗi `ValidationError`

---

### Giai đoạn 4 — Tích hợp & kiểm tra (11:20 – 12:30)

**Người 1:**
- [ ] Hoàn thiện `process_pdf.py` và `process_html.py`
- [ ] Hỗ trợ debug nếu Người 2 gặp lỗi type conversion phức tạp

**Người 2:**
- [ ] Hoàn thiện `process_csv.py` và `process_transcript.py`
- [ ] Chạy từng file riêng lẻ, in kết quả, kiểm tra output hợp lệ

**Người 3:**
- [ ] Hoàn thiện `quality_check.py`:
  - Reject content < 20 ký tự
  - Reject chuỗi toxic (`"Null pointer exception"`, `"Traceback"`, stack trace)
  - Flag discrepancy: `legacy_tax_calc` comment nói 8% nhưng code là 10%
- [ ] Hoàn thiện `orchestrator.py`:
  - Gọi đủ 5 hàm xử lý
  - Chạy `run_quality_gate` trước khi append vào `final_kb`
  - Lưu ra `processed_knowledge_base.json`
  - In thời gian xử lý từng bước (SLA)

---

### Giai đoạn 5 — Forensic & Nộp bài (12:30 – 13:00)

- [ ] **Cả nhóm**: chạy `python orchestrator.py` — kiểm tra `processed_knowledge_base.json` tồn tại và có dữ liệu
- [ ] **Cả nhóm**: chạy `python forensic_agent/agent_forensic.py` — đọc kỹ từng câu hỏi agent hỏi
- [ ] Fix nhanh nếu forensic agent phát hiện lỗi
- [ ] **Từng người commit phần của mình** (điểm cá nhân theo git history)
- [ ] Push lên GitHub

---

## Quy Tắc Phối Hợp

1. **Người 1 commit `schema.py` v1 trước 10:40** — đây là điều kiện tiên quyết để Người 2, 3 import
2. **Khi schema v2 công bố lúc 11:00**: Người 1 phải notify ngay, toàn nhóm dừng để sync
3. **Không hardcode đường dẫn tuyệt đối** — dùng `RAW_DATA_DIR` từ `orchestrator.py`
4. **Commit thường xuyên** — ít nhất 3–5 commit có nghĩa mỗi người (yêu cầu chấm điểm)
5. **Người 3 cần `schema.py` ổn định** trước khi wire orchestrator — nên đợi commit v2 của Người 1

---

## Checklist Nộp Bài Cuối

- [ ] `schema.py` — `UnifiedDocument` v2 hoàn chỉnh
- [ ] `process_pdf.py` — Gemini API chạy được, có retry cho lỗi `429`
- [ ] `process_csv.py` — xử lý duplicate, type trap, date normalization
- [ ] `process_html.py` — bỏ boilerplate, extract bảng `#main-catalog`
- [ ] `process_transcript.py` — loại bỏ noise token, timestamp, tìm giá tiếng Việt
- [ ] `process_legacy_code.py` — extract docstring bằng `ast`, flag tax discrepancy
- [ ] `quality_check.py` — reject ngắn/toxic, flag logic mâu thuẫn
- [ ] `orchestrator.py` — DAG đầy đủ, đo SLA, xuất JSON
- [ ] `processed_knowledge_base.json` — tồn tại, có ít nhất 3 document hợp lệ
- [ ] Forensic agent không báo lỗi nghiêm trọng
- [ ] Mỗi thành viên có ít nhất 3–5 commit có ý nghĩa trên GitHub
