# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Văn Đông
**Nhóm:** Tư duy lệch lạc
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, cho thấy hai đoạn văn thường có nội dung hoặc ý nghĩa tương tự. Giá trị càng gần 1 thì mức tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Người mua có thể yêu cầu hoàn tiền khi sản phẩm bị lỗi.
- Câu B: Khách hàng được phép đề nghị trả lại tiền nếu hàng hóa có khuyết điểm.
- Tại sao tương đồng: Hai câu sử dụng từ ngữ khác nhau nhưng đều nói về quyền yêu cầu hoàn tiền của người mua khi sản phẩm có lỗi.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Người mua có thể yêu cầu hoàn tiền khi sản phẩm bị lỗi.
- Câu B: Người bán phải cung cấp mô tả và giá sản phẩm chính xác.
- Tại sao khác: Câu đầu nói về chính sách hoàn tiền dành cho người mua, còn câu sau nói về trách nhiệm đăng bán sản phẩm của người bán.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung so sánh hướng của hai vector nên phản ánh sự giống nhau về ngữ nghĩa và ít bị ảnh hưởng bởi độ lớn của vector. Khoảng cách Euclid phụ thuộc nhiều vào độ lớn, vì vậy hai vector cùng hướng nhưng có độ dài khác nhau vẫn có thể bị xem là cách xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Phép tính:* Bước dịch giữa hai chunk là `500 - 50 = 450` ký tự. Áp dụng công thức: `ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,11...) = 23`.
>
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, số chunk là `ceil((10.000 - 100) / (500 - 100)) = ceil(9.900 / 400) = 25`, tức tăng từ 23 lên 25 chunks. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới giữa các chunk và giảm nguy cơ tách rời thông tin liên quan, nhưng tạo nhiều dữ liệu trùng lặp hơn, làm tăng chi phí lưu trữ, embedding và truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng đứng sau dấu chấm, chấm than hoặc chấm hỏi, nhờ đó dấu câu vẫn nằm ở cuối câu phía trước. Sau khi tách, tôi loại phần rỗng, `strip()` khoảng trắng rồi ghép tối đa `max_sentences_per_chunk` câu; text rỗng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán lần lượt thử các ranh giới tự nhiên theo độ ưu tiên: đoạn, dòng, câu, từ rồi ký tự; các phần nhỏ được gộp cho đến trước khi vượt `chunk_size`, còn phần quá dài được xử lý đệ quy bằng separator ưu tiên thấp hơn. Base case là text đã không vượt giới hạn thì trả về ngay; nếu hết separator hoặc gặp separator rỗng thì cắt cố định theo `chunk_size`, bảo đảm lời gọi đệ quy luôn tiến gần điều kiện dừng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` sao chép metadata, bổ sung `doc_id` nếu còn thiếu, tạo embedding từ nội dung rồi lưu thành record chuẩn hóa trong store. Khi tìm kiếm, tôi chỉ tạo embedding của query một lần, tính tích vô hướng với embedding của từng record, sắp xếp điểm giảm dần và trả tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc record trước bằng cách yêu cầu mọi cặp key-value trong `metadata_filter` đều khớp, sau đó mới tính similarity trên tập còn lại. `delete_document` tìm và xóa toàn bộ record/chunk có `metadata["doc_id"]` trùng giá trị cần xóa, trả `True` nếu có phần tử bị xóa và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` truy xuất tối đa `top_k` chunk liên quan, đánh số từng đoạn rồi ghép chúng vào phần “Ngữ cảnh” của prompt cùng câu hỏi. Prompt yêu cầu LLM chỉ trả lời dựa trên ngữ cảnh và nói rõ không biết nếu thiếu thông tin; nếu store không trả kết quả, agent cũng chèn thông báo không tìm thấy ngữ cảnh thay vì tạo câu trả lời không có căn cứ.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ .\.venv\Scripts\python.exe -m pytest tests -v
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\VIN_CODEEEEEEEEEEEEEEEEEEEEEEEEE\codelab\DAY07_2A202601310_TranVanDong
collected 42 items

tests/test_solution.py ..........................................       [100%]

============================= 42 passed in 0.15s =============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Người mua có thể yêu cầu hoàn tiền khi sản phẩm bị lỗi. | Khách hàng được phép đề nghị trả lại tiền nếu hàng hóa có khuyết điểm. | cao | 0.084729 | Không |
| 2 | Người bán không được chuyển khách hàng ra ngoài TikTok Shop để giao dịch. | Nhà bán hàng bị cấm hướng người mua sang nền tảng khác để thanh toán. | cao | -0.047460 | Không |
| 3 | Khách hàng có thể thanh toán khi nhận hàng. | Website sử dụng HTTPS để bảo vệ dữ liệu cá nhân. | thấp | 0.102248 | Có |
| 4 | Người mua có 15 ngày sau khi đơn được giao để yêu cầu hoàn tiền. | Thời hạn gửi yêu cầu trả hàng là 15 ngày kể từ trạng thái đã giao. | cao | 0.045741 | Không |
| 5 | Vũ khí và chất nổ thuộc nhóm sản phẩm bị cấm. | Đơn hàng nội thành thường được giao trong vài ngày làm việc. | thấp | 0.187084 | Có |

> Quy ước kiểm tra: điểm cosine từ `0.50` trở lên được xem là cao; thấp hơn `0.50` được xem là thấp. Điểm thực tế được tính bằng `compute_similarity(_mock_embed(câu A), _mock_embed(câu B))` theo backend bắt buộc dùng trong unit test.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 5 ít liên quan lại có điểm cao nhất, trong khi các cặp 1, 2 và 4 gần nghĩa đều có điểm rất thấp. Nguyên nhân là `_mock_embed` tạo vector xác định từ hàm băm để kiểm thử kỹ thuật, không học biểu diễn ngữ nghĩa; vì vậy cần một mô hình embedding tiếng Việt hoặc đa ngôn ngữ thực sự trước khi kết luận về chất lượng retrieval.

---

## 5. Kết quả truy xuất & Phân tích thất bại (Competition Results & Failure Analysis) — Cá nhân (10 điểm)

### Ghi chú về Embedder và cấu hình thực nghiệm

- **Embedder sử dụng:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, mô hình embedding đa ngữ chạy cục bộ.
- **Agent/LLM function:** dùng `extractive_llm` cục bộ trong `bench.py` để trả lại nội dung Top-1; không dùng API sinh văn bản. Vì vậy phép đo tập trung vào retrieval, chunk-level evidence và grounding.
- **Strategy cá nhân:** `RecursiveChunker(chunk_size=300)`; implementation hiện tại không có overlap.
- **Corpus:** 10 file trong `data/k4_ecommerce`, sau khi bỏ front matter và chunk tạo thành **75 chunks**.
- **Điều kiện so sánh:** dùng đúng 5 query và gold answer chung của nhóm; áp dụng pre-filter theo `customer_role` rồi mới xếp hạng vector.

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời hạn tối đa để Người mua gửi yêu cầu trả hàng/hoàn tiền là bao lâu? (`customer_role=buyer`) | `returns-policy::chunk_2`: yêu cầu trong 15 ngày kể từ ngày nhận hàng thành công | 0.7762 | Có; chứa đủ mốc thời gian và điều kiện | Trả lời đúng 15 ngày và sau hạn hệ thống tắt nút yêu cầu |
| 2 | Người bán có được đăng vũ khí, bình xịt hơi cay hoặc thuốc kê đơn không? (`customer_role=seller`) | `seller-listing::chunk_5`: cấm vũ khí, trong đó có bình xịt hơi cay | 0.6289 | Liên quan nhưng thiếu phần thuốc kê đơn | Trả lời đúng phần vũ khí/bình xịt, thiếu thuốc kê đơn |
| 3 | Hoàn tiền vào Ví điện tử và Thẻ tín dụng quốc tế mất bao lâu? (`customer_role=both`) | `payment-policy::chunk_7`: thẻ quốc tế mất 5–7 ngày làm việc | 0.7736 | Liên quan nhưng chỉ chứa một trong hai kênh | Trả lời 5–7 ngày cho thẻ nhưng thiếu 24 giờ cho Ví |
| 4 | Tỷ lệ hủy đơn của Người bán vượt 10% bị cộng bao nhiêu điểm? (`customer_role=seller`) | `seller-penalties::chunk_2`: vượt 10% cộng 2 điểm; vượt 15% cộng 3 điểm | 0.8631 | Có; chứa đủ điều kiện và ngoại lệ | Trả lời đúng 2 điểm và nêu đúng ngưỡng 15%/3 điểm |
| 5 | Người mua có quyền đồng kiểm không và bị cấm làm gì? (`customer_role=buyer`) | `shipping-warranty::chunk_2`: được mở kiện để kiểm tra ngoại quan | 0.7874 | Liên quan nhưng thiếu các hành vi bị cấm | Trả lời đúng quyền kiểm tra, thiếu cấm bóc tem/cắm điện/làm rách bao bì |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 theo `doc_id`; 3 / 5 khi bắt buộc Top-3 chứa đủ các chuỗi bằng chứng của gold answer.

### Kiểm tra Top-3 ở mức bằng chứng

Tôi dùng `RecursiveChunker(chunk_size=300)` và mô hình `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Corpus tạo ra 75 chunks. Kết quả chi tiết được sinh bởi `bench.py`:

| # | Top-3 (`doc_id:chunk_index`, score) | Đủ bằng chứng? | Điểm rubric |
|---|---|---|---|
| 1 | `returns-policy:2` (0.7762); `tiktok-virtual-items:1` (0.7524); `returns-policy:9` (0.7421) | Có: `15 ngày` và `nhận hàng thành công` | 2/2 |
| 2 | `seller-listing:5` (0.6289); `seller-listing:0` (0.6240); `seller-listing:4` (0.5170) | Không: có `bình xịt hơi cay` nhưng thiếu `thuốc kê đơn` | 1/2 |
| 3 | `payment-policy:7` (0.7736); `payment-policy:6` (0.7229); `payment-policy:5` (0.5852) | Có trong Top-3, nhưng hai mốc nằm ở hai chunk và Agent chỉ trích Top-1 | 1/2 |
| 4 | `seller-penalties:2` (0.8631); `seller-penalties:1` (0.7635); `tiktok-community-guidelines:4` (0.6707) | Có: `10%` và `2 điểm phạt` cùng nằm trong Top-1 | 2/2 |
| 5 | `shipping-warranty:2` (0.7874); `shipping-warranty:5` (0.6890); `shipping-warranty:0` (0.6742) | Không: có quyền kiểm tra ngoại quan nhưng thiếu đoạn giới hạn đồng kiểm | 1/2 |

**Tổng điểm retrieval + agent theo rubric:** 7 / 10.

### Thực nghiệm A/B: Metadata Filter

| # | Filter | Top-3 WITH FILTER | Top-3 WITHOUT FILTER | Nhận xét |
|---|---|---|---|---|
| 1 | `customer_role=buyer` | `returns-policy`, `tiktok-virtual-items`, `returns-policy` | Giống WITH FILTER | Query đã nêu rõ người mua nên filter không thay đổi thứ hạng. |
| 2 | `customer_role=seller` | Ba chunk `seller-listing` | Hai chunk `seller-listing`, một `shipping-warranty` | Filter loại một tài liệu sai vai trò nhưng Top-3 vẫn thiếu bằng chứng `thuốc kê đơn`. |
| 3 | `customer_role=both` | Ba chunk `payment-policy` | Hai chunk `payment-policy`, một `returns-policy` | Filter loại tài liệu buyer và làm tập kết quả đồng nhất hơn. |
| 4 | `customer_role=seller` | Hai `seller-penalties`, một `tiktok-community-guidelines` | Giống WITH FILTER | Query đã nêu rõ người bán và từ khóa điểm phạt đủ đặc trưng. |
| 5 | `customer_role=buyer` | Ba chunk `shipping-warranty` | Hai `shipping-warranty`, một `tiktok-terms-of-service` | Filter giảm nhiễu nhưng vẫn không đưa chunk giới hạn đồng kiểm vào Top-3. |

Kết quả A/B cho thấy metadata giảm nhiễu ở Câu 2, 3 và 5; Câu 1 và 4 không thay đổi. Filter cải thiện precision theo vai trò nhưng không tự bảo đảm các chunk còn lại chứa đủ bằng chứng.

### Trả lời các câu hỏi phân tích chất lượng

1. **Precision:** Cả 5/5 câu có đúng `doc_id` trong Top-3, nhưng chỉ 3/5 câu có đủ toàn bộ chuỗi bằng chứng. Điều này chứng minh score và đúng tài liệu chưa đủ để kết luận retrieval trả lời được query.
2. **Chunk coherence:** RecursiveChunker thường giữ nguyên ranh giới đoạn/dòng, nhưng `chunk_size=300` vẫn tách các câu hỏi nhiều ý. Câu 3 tách mốc hoàn Ví và hoàn Thẻ sang hai chunks; Câu 5 tách quyền đồng kiểm khỏi các hành vi bị cấm.
3. **Metadata utility:** Pre-filter hữu ích ở 3/5 câu khi loại chunk sai vai trò. Tuy nhiên filter không sửa được lỗi thiếu bằng chứng bên trong tài liệu đúng.
4. **Grounding:** Agent trích xuất nội dung từ Top-1 nên các câu trả lời không bịa ngoài context. Đổi lại, Câu 3 và 5 bị thiếu ý dù thông tin có thể nằm ở chunk khác hoặc ngoài Top-3; kết quả retrieval vẫn truy vết được qua `doc_id` và `chunk_index`.
5. **Failure case:** Hai failure dưới đây xuất phát từ ranh giới chunk và cách Agent tổng hợp context, không thể giải thích đơn giản là “model sai”.

#### Failure Case 1 — Hai mốc hoàn tiền bị tách (Câu 3)

- **Query:** thời gian hoàn tiền vào Ví điện tử và Thẻ tín dụng quốc tế.
- **Bằng chứng Top-k:** Rank 1 `payment-policy::chunk_7` (0.7736) chứa `5 đến 7 ngày làm việc` cho Thẻ; Rank 2 `payment-policy::chunk_6` (0.7229) chứa `24 giờ làm việc` cho Ví.
- **Hiện tượng:** Top-3 có đủ bằng chứng khi ghép lại, nhưng Agent chỉ trích Top-1 nên trả lời thiếu mốc 24 giờ.
- **Nguyên nhân:** Hai ý của cùng một mục vượt ranh giới chunk; pipeline trả nhiều đoạn nhưng hàm LLM trích xuất chưa tổng hợp chúng.
- **Đề xuất:** dùng heading-aware chunker để gắn lại tiêu đề mục vào các mảnh con, hoặc cải tiến Agent để tổng hợp mọi chunk Top-3 trước khi trả lời.

#### Failure Case 2 — Thiếu giới hạn đồng kiểm (Câu 5)

- **Query:** người mua có quyền mở kiện đồng kiểm không và bị cấm làm gì.
- **Bằng chứng Top-k:** Rank 1 `shipping-warranty::chunk_2` (0.7874) chứa quyền kiểm tra ngoại quan; Rank 2 `shipping-warranty::chunk_5` (0.6890) nói về video unbox; Rank 3 `shipping-warranty::chunk_0` (0.6742) chỉ là tiêu đề. Không chunk nào trong Top-3 chứa `nghiêm cấm bóc tem`.
- **Hiện tượng:** retrieval đúng file nhưng Agent chỉ trả lời được nửa đầu câu hỏi.
- **Nguyên nhân:** `chunk_size=300` không overlap tách quyền và giới hạn đồng kiểm; cosine ưu tiên các chunk lặp từ khóa query hơn chunk chứa danh sách cấm.
- **Đề xuất:** bổ sung overlap trong RecursiveChunker hoặc dùng heading-aware chunker để giữ các gạch đầu dòng liên quan dưới cùng tiêu đề.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua trao đổi với thành viên sử dụng `FixedSizeChunker`, tôi nhận thấy hai strategy có cách xác định ranh giới khác nhau: FixedSizeChunker cắt theo số ký tự cố định, còn `RecursiveChunker(size=300)` của tôi ưu tiên ranh giới đoạn, dòng, câu và từ. Kết quả cá nhân cũng cho tôi thấy cần chấm bằng chuỗi bằng chứng trong chunk thay vì chỉ nhìn `doc_id` hoặc score; hiệu quả của metadata filter phải được kiểm tra A/B thực tế thay vì mặc định rằng có filter luôn tốt hơn.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
