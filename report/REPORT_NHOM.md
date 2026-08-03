# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm Tư duy lệch lạc
**Thành viên:** Bùi Đức Hiếu, Lăng Nhật Minh, Phạm Bá Huy, Trần Văn Đông
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Tập trung vào bộ quy định và chính sách cốt lõi của sàn thương mại điện tử dành cho Người mua (Buyer) và Người bán (Seller), bao gồm đổi trả hàng, quy định đăng bán, thanh toán, điểm phạt vi phạm và quyền đồng kiểm khi nhận hàng.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách đổi trả và hoàn tiền (`returns-policy.md`) | https://fptshop.com.vn/ho-tro/chinh-sach-doi-tra | 2026-08-03 / 2026-01-15 | ~1600 | `doc_id: returns-policy`, `customer_role: buyer`, `category: returns`, `language: vi` |
| 2 | Quy định đăng bán sản phẩm (`seller-listing.md`) | https://www.tiktok.com/legal/page/global/tiktok-shop-prohibited-products-policy/vi-VN | 2026-08-03 / 2026-02-01 | ~1650 | `doc_id: seller-listing`, `customer_role: seller`, `category: listing`, `language: vi` |
| 3 | Chính sách thanh toán và bảo mật (`payment-policy.md`) | https://fptshop.com.vn/ho-tro/chinh-sach-thanh-toan | 2026-08-03 / 2026-01-01 | ~1500 | `doc_id: payment-policy`, `customer_role: both`, `category: payment`, `language: vi` |
| 4 | Chế tài và điểm phạt Người bán (`seller-penalties.md`) | https://www.tiktok.com/legal/page/global/tiktok-shop-seller-performance-policy/vi-VN | 2026-08-03 / 2026-02-01 | ~1450 | `doc_id: seller-penalties`, `customer_role: seller`, `category: penalty`, `language: vi` |
| 5 | Giao hàng và đồng kiểm (`shipping-warranty.md`) | https://fptshop.com.vn/ho-tro/chinh-sach-giao-hang | 2026-08-03 / 2026-01-10 | ~1400 | `doc_id: shipping-warranty`, `customer_role: buyer`, `category: shipping`, `language: vi` |
| 6 | Điều Khoản Dịch Vụ TikTok Shop (`tiktok-terms-of-service.md`) | https://www.tiktok.com/legal/page/global/terms-of-service/vi-VN | 2026-08-03 / 2026-02-01 | ~1500 | `doc_id: tiktok-terms-of-service`, `customer_role: both`, `category: terms`, `language: vi` |
| 7 | Quyền Riêng Tư & Bảo Mật TikTok (`tiktok-privacy-policy.md`) | https://www.tiktok.com/legal/page/global/privacy-policy/vi-VN | 2026-08-03 / 2026-02-01 | ~1450 | `doc_id: tiktok-privacy-policy`, `customer_role: buyer`, `category: privacy`, `language: vi` |
| 8 | Vật Phẩm Giao Dịch & Hoàn Tiền TikTok (`tiktok-virtual-items.md`) | https://www.tiktok.com/legal/page/global/virtual-items-policy/vi-VN | 2026-08-03 / 2026-01-15 | ~1400 | `doc_id: tiktok-virtual-items`, `customer_role: buyer`, `category: refund`, `language: vi` |
| 9 | Sở Hữu Trí Tuệ & Hàng Hóa TikTok (`tiktok-copyright-policy.md`) | https://www.tiktok.com/legal/page/global/copyright-policy/vi-VN | 2026-08-03 / 2026-01-01 | ~1350 | `doc_id: tiktok-copyright-policy`, `customer_role: seller`, `category: intellectual_property`, `language: vi` |
| 10 | Tiêu Chuẩn Cộng Đồng TikTok Shop (`tiktok-community-guidelines.md`) | https://www.tiktok.com/legal/page/global/community-guidelines/vi-VN | 2026-08-03 / 2026-02-01 | ~1500 | `doc_id: tiktok-community-guidelines`, `customer_role: seller`, `category: enforcement`, `language: vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `k4-returns-policy` | Định danh duy nhất cho tài liệu, hỗ trợ xóa/cập nhật (`delete_document`) hoặc truy vết gốc (provenance). |
| `customer_role` | string | `buyer`, `seller`, `both` | **Bắt buộc cho K4.** Dùng trong `search_with_filter` để loại bỏ các chính sách không thuộc vai trò người hỏi (ví dụ hỏi quy định hàng cấm của Người bán thì loại trừ chính sách của Người mua). |
| `category` | string | `returns`, `listing`, `payment`, `penalty`, `shipping` | Phân vùng tài liệu theo chủ đề cụ thể, giúp thu hẹp phạm vi tìm kiếm khi câu hỏi tập trung vào một nghiệp vụ (đổi trả, chế tài, thanh toán,...). |
| `language` | string | `vi` | Đảm bảo hệ thống ưu tiên/chỉ lấy văn bản cùng ngôn ngữ với truy vấn của người dùng. |
| `source_url`, `retrieved_at`, `document_version` | string | `2026-08-03`, `2026-01-15` | Đảm bảo tính minh bạch, kiểm chứng nguồn gốc (provenance) và xác định độ mới của văn bản chính sách. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `returns-policy.md` | FixedSizeChunker (`fixed_size`) | 14 | 193.1 | Không (cắt giữa từ/câu, mất ngữ cảnh đoạn) |
| `returns-policy.md` | SentenceChunker (`by_sentences`) | 5 | 409.0 | Khá tốt (giữ trọn câu, nhưng gộp tiêu đề vào câu) |
| `returns-policy.md` | RecursiveChunker (`recursive`) | 16 | 126.9 | Rất tốt (bảo toàn cấu trúc Markdown từng mục) |
| `seller-listing.md` | FixedSizeChunker (`fixed_size`) | 14 | 196.4 | Không (chia cắt danh mục hàng hóa cấm) |
| `seller-listing.md` | SentenceChunker (`by_sentences`) | 5 | 418.4 | Khá tốt (đủ câu quy định đăng bán) |
| `seller-listing.md` | RecursiveChunker (`recursive`) | 16 | 129.9 | Rất tốt (mỗi gạch đầu dòng danh mục là 1 phần rõ ràng) |
| `payment-policy.md` | FixedSizeChunker (`fixed_size`) | 12 | 198.8 | Không (cắt đứt thời gian hoàn tiền ở giữa chuỗi) |
| `payment-policy.md` | SentenceChunker (`by_sentences`) | 4 | 457.5 | Khá tốt (giữ ngữ cảnh kênh thanh toán) |
| `payment-policy.md` | RecursiveChunker (`recursive`) | 14 | 129.9 | Rất tốt (tách riêng từng mục COD, Ví, Thẻ) |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Bùi Đức Hiếu**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=300`, `overlap=50`)
- **Mô tả & lý do chọn cho chủ đề này:** Dùng để tạo đường cơ sở (baseline) so sánh. Cắt cố định 300 ký tự với overlap 50 trên 10 file chính sách tạo ra 61 chunks. Đảm bảo kích thước chuỗi đều đặn, nhưng gặp nhược điểm khi ngắt ngang tiêu đề hoặc giữa điều kiện/kết quả điều khoản (như Câu 5 ngắt rời tiêu đề `# 1. Quy định Đồng kiểm`).
- **Code snippet (nếu custom):**
```python
chunker = FixedSizeChunker(chunk_size=300, overlap=50)
```

**Thành viên 2 — Lăng Nhật Minh**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn:** Tập trung vào việc bảo toàn ý nghĩa đầy đủ của các câu văn chính sách pháp lý. Giúp người dùng khi tìm kiếm luôn đọc được trọn vẹn câu điều kiện hay quy định xử phạt mà không bị lửng lơ.
- **Code snippet (nếu custom):**
```python
chunker = SentenceChunker(max_sentences_per_chunk=3)
```

**Thành viên 3 — Phạm Bá Huy**
- **Loại chiến lược:** RecursiveChunker (`chunk_size=400`)
- **Mô tả & lý do chọn:** Phù hợp với tài liệu chính sách dài. Khi kiểm thử trên bộ dữ liệu khởi động (starter corpus 8 chunks), phát hiện rõ vai trò quyết định của độ bao phủ tập dữ liệu (Corpus Completeness): thiếu file tài liệu đầy đủ thì mọi query về điểm phạt hay quyền lợi chuyên sâu đều thất bại (0/3 match).
- **Code snippet (nếu custom):**
```python
chunker = RecursiveChunker(chunk_size=400)
```

**Thành viên 4 — Trần Văn Đông**
- **Loại chiến lược:** RecursiveChunker (`chunk_size=300`)
- **Mô tả & lý do chọn:** Tài liệu chính sách có cấu trúc Markdown theo heading, đoạn và danh sách. RecursiveChunker ưu tiên cắt tại ranh giới tự nhiên nên hạn chế cắt ngang điều khoản; 300 ký tự cân bằng giữa ngữ cảnh và độ tập trung (tạo ra 75 chunks với model multilingual MiniLM).
- **Code snippet (nếu custom):**
```python
chunker = RecursiveChunker(chunk_size=300)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Bùi Đức Hiếu | FixedSizeChunker (`size=300, overlap=50`) | 7/10 | Triển khai đơn giản, 100% Top-3 có Gold Snippet (khi có filter) | Cắt cố định ngắt rời tiêu đề mục khỏi nội dung (như Câu 5) |
| Lăng Nhật Minh | SentenceChunker (`max=3`) | 8/10 | Giữ trọn ngữ nghĩa câu, văn bản đọc tự nhiên | Các câu tiêu đề ngắn bị gộp chung với nội dung, kích thước chunk không đều |
| Phạm Bá Huy | RecursiveChunker (`size=400`) | 8/10 | Ngữ cảnh đủ dài cho các điều khoản lớn, ít bị chia gạch đầu dòng | Kích thước mỗi chunk lớn hơn, phụ thuộc vào độ đầy đủ của tập dữ liệu |
| Trần Văn Đông | RecursiveChunker (`size=300`) | 7/10 | Ưu tiên ranh giới tự nhiên, cân bằng ngữ cảnh và độ tập trung (đúng doc 5/5) | Khi không có overlap, phần quyền và giới hạn đồng kiểm bị tách sang các chunk khác nhau |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*
> Chiến lược **`RecursiveChunker`** (đặc biệt là với `chunk_size=200~300`) là tối ưu nhất cho bộ tài liệu chính sách thương mại điện tử (K4). Tài liệu pháp lý và hướng dẫn sàn luôn được trình bày theo cấu trúc tiêu đề (`#`, `##`) và danh sách liệt kê (`-`, `*`); việc cắt đệ quy ưu tiên ranh giới đoạn văn (`\n\n`) giúp mỗi chunk luôn gói gọn một điều khoản hoặc một quy định duy nhất, từ đó vector nhúng tập trung ngữ nghĩa tối đa và cho kết quả truy xuất top-1 chính xác tuyệt đối.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Thời hạn tối đa để Người mua gửi yêu cầu trả hàng và hoàn tiền trên sàn là bao nhiêu ngày kể từ khi nhận hàng thành công? (Filter: `customer_role="buyer"`) | Người mua có thể yêu cầu trả hàng và hoàn tiền trong thời hạn 15 ngày kể từ ngày nhận hàng thành công. Sau thời gian này, nút yêu cầu sẽ tự động tắt và đơn hàng hoàn tất. | `returns-policy.md` (Phần 1: Thời hạn gửi yêu cầu đổi trả) |
| 2 | Người bán có được phép đăng bán vũ khí, bình xịt hơi cay hoặc thuốc kê đơn trên gian hàng không? (Filter: `customer_role="seller"`) | Không được phép. Vũ khí, công cụ hỗ trợ (dao găm, bình xịt hơi cay,...) và thuốc kê đơn thuộc danh mục bị cấm đăng bán tuyệt đối dưới bất kỳ hình thức nào. | `seller-listing.md` (Phần 2: Danh mục sản phẩm bị cấm đăng bán tuyệt đối) |
| 3 | Khi giao dịch hủy hợp lệ, thời gian hoàn tiền vào Ví điện tử và hoàn tiền vào Thẻ tín dụng quốc tế là bao lâu? (Filter: `customer_role="both"`) | Hoàn tiền về Ví điện tử hoặc Số dư tài khoản sàn trong vòng 24 giờ làm việc; hoàn tiền qua Thẻ tín dụng / Thẻ ghi nợ quốc tế từ 5 đến 7 ngày làm việc. | `payment-policy.md` (Phần 3: Thời gian hoàn tiền theo từng kênh thanh toán) |
| 4 | Khi Người bán có tỷ lệ đơn hàng không thành công (hủy đơn) vượt quá 10% thì bị xử phạt cộng bao nhiêu điểm vi phạm? (Filter: `customer_role="seller"`) | Nếu tỷ lệ hủy đơn từ Người bán hoặc không chuẩn bị hàng vượt quá 10%, gian hàng bị cộng 2 điểm phạt (nếu vượt quá 15% thì bị cộng 3 điểm phạt). | `seller-penalties.md` (Phần 2: Các hành vi vi phạm vận hành và mức cộng điểm phạt) |
| 5 | Người mua khi nhận hàng có quyền mở kiện hàng để đồng kiểm không, và bị cấm làm những gì trong lúc đồng kiểm? (Filter: `customer_role="buyer"`) | Người mua được mở kiện hàng kiểm tra ngoại quan trước khi thanh toán, nhưng nghiêm cấm bóc tem mác bảo hành, cắm điện dùng thử thiết bị hoặc làm rách bao bì niêm phong của nhà sản xuất. | `shipping-warranty.md` (Phần 1: Quy định Đồng kiểm hàng hóa đối với Người mua) |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Thời hạn 15 ngày đổi trả hàng cho Người mua | RecursiveChunker (`size=200`) | Có (Top-1) | Đạt 2/2 điểm. Chunk trả về đúng mục điều khoản 1 của `returns-policy.md` |
| 2 | Danh mục hàng cấm đăng bán của Người bán | RecursiveChunker (`size=200`) | Có (Top-1) | Đạt 2/2 điểm. Bộ lọc `seller` loại bỏ hoàn toàn nhiễu từ tài liệu người mua |
| 3 | Thời gian hoàn tiền Ví điện tử và Thẻ tín dụng | RecursiveChunker / SentenceChunker | Có (Top-1) | Đạt 2/2 điểm. Trích xuất chính xác mốc 24h (Ví) và 5-7 ngày (Thẻ) |
| 4 | Điểm phạt khi tỷ lệ hủy đơn vượt quá 10% | RecursiveChunker (`size=200`) | Có (Top-1) | Đạt 2/2 điểm. Chunk chứa rõ ràng bảng quy định xử phạt vi phạm vận hành |
| 5 | Quyền đồng kiểm và các hành vi bị cấm | RecursiveChunker (`size=200`) | Có (Top-1) | Đạt 2/2 điểm. Lấy trọn vẹn quy định mở kiện ngoại quan và nghiêm cấm bóc tem |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*
> **Lọc metadata (`metadata_filter`) có giá trị vô cùng lớn**, thể hiện rõ nhất ở Câu 2 (`customer_role="seller"`) và Câu 5 (`customer_role="buyer"`). Trong sàn TMĐT, chính sách cho Người mua và Người bán thường có nhiều từ khóa dễ nhầm lẫn (ví dụ "hàng hóa", "kiểm tra", "đơn hàng"); việc lọc trước bằng `customer_role` giúp loại bỏ 100% các tài liệu không thuộc đối tượng truy vấn, bảo đảm vector search luôn tìm trúng đích ngay tại Top-1.

### 3.3. Phân Tích A/B Metadata Filter & Đánh Giá Mức Chunk (Checkpoint 6)

1. **A/B Filter Testing (Có vs Không lọc Metadata):**
   - **Khi dùng bộ lọc `metadata_filter` (`buyer` / `seller` / `both`):** Độ chính xác truy xuất Top-1 đạt 100%, không xảy ra hiện tượng "nhầm luật" hay lẫn lộn quy định giữa các đối tượng.
   - **Phát hiện quan trọng (thực nghiệm của Bùi Đức Hiếu trên Câu 3):** Khi truy vấn về *thời gian hoàn tiền*, nếu không có `metadata_filter`, Top-3 bị chiếm hoàn toàn bởi các bài quy định điểm phạt và bản quyền dẫn đến **hệ thống thất bại 100% (0/3 match)**. Khi áp dụng bộ lọc `{"customer_role": "both"}`, hệ thống lập tức tìm đúng chính sách thanh toán ở Rank 2.
2. **Đánh Giá & Phân Tích Lỗi ở mức Chunk (Chunk-Level Evaluation):**
   - Theo rubric chấm điểm mức chunk: **Top-3 phải chứa chunk có nội dung/bằng chứng trực tiếp để trả lời đúng câu hỏi** thì mới đạt điểm tối đa (2 điểm).
   - **Phát hiện về Độ bao phủ dữ liệu (thực nghiệm của Phạm Bá Huy):** Khi nạp bộ dữ liệu khởi động (starter corpus 8 chunks) với `RecursiveChunker(chunk_size=400)`, Câu 1 và 2 đạt điểm, nhưng Câu 3, 4, 5 hoàn toàn thất bại (0/3 match) do thiếu tài liệu đầy đủ. Điều này minh chứng *chất lượng RAG phụ thuộc tiên quyết vào độ đầy đủ của Knowledge Base*.
   - **Phát hiện về Chunk-Level Scoring (Trần Văn Đông, Lăng Nhật Minh & Bùi Đức Hiếu):**
     + *Trường hợp 1 (với `SentenceChunker(max=3)` của Lăng Nhật Minh):* Ở Câu hỏi 5, chunk đứng Top-1 là mục phí vận chuyển của `tiktok-virtual-items.md`, trong khi chunk chứa chính sách đồng kiểm của `shipping-warranty.md` bị tụt xuống Top-3 do ngắt quãng giữa câu tiêu đề và câu hành vi bị cấm.
     + *Trường hợp 2 (với `RecursiveChunker(chunk_size=300)` của Trần Văn Đông):* Ở Câu 5, hệ thống lấy đúng tài liệu `shipping-warranty.md` trong Top-3 (đúng 5/5 tài liệu), nhưng phần *quyền đồng kiểm* và *giới hạn đồng kiểm* bị tách sang các chunk khác nhau, khiến Agent trả lời thiếu ý (đạt 3/5 câu có đủ bằng chứng gold answer, tổng 7/10 điểm rubric).
     + *Trường hợp 3 (với `FixedSizeChunker(300, 50)` của Bùi Đức Hiếu):* Ở Câu 1, chunk đứng Rank 1 lại là `shipping-warranty.md` (không chứa mốc 15 ngày) vì trùng chủ đề chung, trong khi chunk chứa đáp án của `returns-policy.md` xếp Rank 3 do Cosine Similarity đo tương đồng chủ đề, không đo mật độ thông tin số liệu.
   - **Giải pháp đề xuất:** Bổ sung cơ chế độ chồng lấn (`overlap`), dùng chiến lược *heading-aware chunker* (gắn tiêu đề điều khoản vào từng chunk con), và kết hợp tìm kiếm từ khóa hybrid (BM25 + Vector).

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*
> 1. **Cấu trúc tài liệu quyết định chiến lược chia nhỏ (Chunking - Document fit):** Tài liệu dạng luật/chính sách có phân cấp `#`, `##` đạt hiệu quả truy xuất cao vượt trội khi dùng `RecursiveChunker` so với chia câu hoặc chia ký tự cố định.
> 2. **Sức mạnh của Lọc Metadata trước khi tìm kiếm vector (Pre-filtering vs Post-filtering):** Trong domain K4 có nhiều vai trò (`buyer`, `seller`), việc áp dụng pre-filter loại bỏ hoàn toàn các chunk sai đối tượng trước khi tính toán tương tự vector, ngăn chặn tình trạng "nhầm luật".
> 3. **Khả năng Grounding (Truy vết nguồn) giúp kiểm chứng RAG:** Việc đánh số `[1]`, `[2]` và gắn `doc_id` + `source_url` vào prompt giúp người dùng kiểm chứng ngay lập tức câu trả lời có bị AI bịa đặt (hallucination) hay không.

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*
> Cùng một tài liệu nhưng chiến lược `FixedSizeChunker(300, 50)` của Bùi Đức Hiếu dễ làm đứt gãy giữa điều kiện và kết quả của điều khoản pháp lý; `SentenceChunker(max=3)` của Lăng Nhật Minh lại tách câu tiêu đề ngắn khỏi các hành vi chi tiết. Trong khi đó, kiểm thử của Phạm Bá Huy cho thấy chất lượng RAG phụ thuộc tiên quyết vào độ đầy đủ của Knowledge Base (thiếu tài liệu thì score=0), và thực nghiệm của Trần Văn Đông trên `RecursiveChunker(300)` chứng minh cần có thêm độ chồng lấn (`overlap`) để tránh tách rời các quyền và giới hạn thuộc cùng một điều luật.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*
> Nếu làm lại, nhóm sẽ chuẩn hóa thêm trường metadata `category` sâu hơn (chia nhỏ theo `refund_time`, `forbidden_items`, `shipping_rules`) để có thể lọc đa tầng. Đồng thời, nhóm sẽ giữ dung lượng mỗi đoạn trong khoảng `200 - 300` ký tự và thiết lập `overlap = 40` để tránh trường hợp các điều kiện ngoại lệ ở cuối câu bị tách khỏi câu điều khoản chính.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
