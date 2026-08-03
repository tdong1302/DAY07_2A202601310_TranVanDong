"""Benchmark CP5 cho thành viên K4.

Chạy bằng PowerShell:
    $env:PYTHONUTF8="1"
    python bench.py
"""
from __future__ import annotations

import re
import sys

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import LocalEmbedder


# Giữ tiếng Việt đúng trên cả Windows PowerShell cũ dùng code page cp1252.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


DATA_DIR = "data/k4_ecommerce"
STRATEGY = "RecursiveChunker(chunk_size=300)"

# Bộ câu hỏi đã chốt trong report/REPORT_NHOM.md. Không thay đổi sau khi chạy.
BENCHMARKS = [
    {
        "query": "Thời hạn tối đa để Người mua gửi yêu cầu trả hàng và hoàn tiền trên sàn là bao nhiêu ngày kể từ khi nhận hàng thành công?",
        "role": "buyer",
        "expected_doc": "returns-policy",
        "gold": "15 ngày kể từ ngày nhận hàng thành công.",
        "evidence": ["15 ngày", "nhận hàng thành công"],
    },
    {
        "query": "Người bán có được phép đăng bán vũ khí, bình xịt hơi cay hoặc thuốc kê đơn trên gian hàng không?",
        "role": "seller",
        "expected_doc": "seller-listing",
        "gold": "Không; vũ khí, bình xịt hơi cay và thuốc kê đơn thuộc danh mục bị cấm.",
        "evidence": ["bình xịt hơi cay", "thuốc kê đơn"],
    },
    {
        "query": "Khi giao dịch hủy hợp lệ, thời gian hoàn tiền vào Ví điện tử và hoàn tiền vào Thẻ tín dụng quốc tế là bao lâu?",
        "role": "both",
        "expected_doc": "payment-policy",
        "gold": "Ví điện tử trong 24 giờ làm việc; thẻ quốc tế từ 5 đến 7 ngày làm việc.",
        "evidence": ["24 giờ làm việc", "5 đến 7 ngày làm việc"],
    },
    {
        "query": "Khi Người bán có tỷ lệ đơn hàng không thành công (hủy đơn) vượt quá 10% thì bị xử phạt cộng bao nhiêu điểm vi phạm?",
        "role": "seller",
        "expected_doc": "seller-penalties",
        "gold": "Cộng 2 điểm phạt; nếu vượt 15% thì cộng 3 điểm.",
        "evidence": ["10%", "2 điểm phạt"],
    },
    {
        "query": "Người mua khi nhận hàng có quyền mở kiện hàng để đồng kiểm không, và bị cấm làm những gì trong lúc đồng kiểm?",
        "role": "buyer",
        "expected_doc": "shipping-warranty",
        "gold": "Được kiểm tra ngoại quan; không được bóc tem bảo hành, cắm điện dùng thử hoặc làm rách bao bì niêm phong.",
        "evidence": ["kiểm tra ngoại quan", "nghiêm cấm bóc tem"],
    },
]


class FilteredStoreView:
    """Cho KnowledgeBaseAgent dùng cùng metadata filter như lượt benchmark."""

    def __init__(self, store, metadata_filter: dict[str, str]) -> None:
        self.store = store
        self.metadata_filter = metadata_filter

    def search(self, query: str, top_k: int = 3):
        return self.store.search_with_filter(
            query, top_k=top_k, metadata_filter=self.metadata_filter
        )


def extractive_llm(prompt: str) -> str:
    """LLM giả lập không cần API: trả đoạn Top-1 để kiểm tra grounding."""
    match = re.search(
        r"\[Đoạn 1\]\n(.*?)(?=\n\n\[Đoạn 2\]|\n\nCâu hỏi:)",
        prompt,
        flags=re.S,
    )
    if not match:
        return "Không tìm thấy ngữ cảnh liên quan trong cơ sở tri thức."
    answer = " ".join(match.group(1).split())
    return answer[:500]


def main() -> int:
    print("=== CHECKPOINT 5 — BENCHMARK K4 ===")
    print(f"Corpus   : {DATA_DIR}")
    print(f"Strategy : {STRATEGY}")

    embedder = LocalEmbedder()
    print(f"Embedder : {embedder._backend_name}")

    # Đây là dòng strategy riêng của thành viên K4.
    chunker = RecursiveChunker(chunk_size=300)
    store = build_knowledge_base(
        DATA_DIR,
        embedding_fn=embedder,
        chunker=chunker,
        collection_name="k4_cp5_benchmark",
    )
    print(f"Số chunk : {store.get_collection_size()}")

    doc_hits = 0
    evidence_hits = 0
    rubric_points = 0
    for index, item in enumerate(BENCHMARKS, start=1):
        metadata_filter = {"customer_role": item["role"]}
        results = store.search_with_filter(
            item["query"], top_k=3, metadata_filter=metadata_filter
        )
        doc_hit = any(
            result["metadata"].get("doc_id") == item["expected_doc"]
            for result in results
        )
        doc_hits += int(doc_hit)
        combined_context = "\n".join(result["content"] for result in results).casefold()
        evidence_hit = all(term.casefold() in combined_context for term in item["evidence"])
        evidence_hits += int(evidence_hit)

        unfiltered = store.search(item["query"], top_k=3)
        filtered_ids = [result["metadata"].get("doc_id") for result in results]
        unfiltered_ids = [result["metadata"].get("doc_id") for result in unfiltered]

        print("\n" + "=" * 88)
        print(f"CÂU {index}: {item['query']}")
        print(f"Filter  : {metadata_filter}")
        print(f"Gold    : {item['gold']}")
        print(f"Top-3 có đúng doc ({item['expected_doc']}): {'CÓ' if doc_hit else 'KHÔNG'}")
        print(f"Top-3 có đủ bằng chứng {item['evidence']}: {'CÓ' if evidence_hit else 'KHÔNG'}")
        print(f"A/B doc_id — có filter: {filtered_ids}")
        print(f"A/B doc_id — không lọc : {unfiltered_ids}")
        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]
            preview = " ".join(result["content"].split())[:220]
            print(
                f"  Top-{rank}: score={result['score']:.4f} "
                f"doc_id={metadata.get('doc_id')} "
                f"chunk_index={metadata.get('chunk_index')}"
            )
            print(f"         {preview}")

        agent = KnowledgeBaseAgent(
            store=FilteredStoreView(store, metadata_filter),
            llm_fn=extractive_llm,
        )
        agent_answer = agent.answer(item["query"], top_k=3)
        answer_correct = all(term.casefold() in agent_answer.casefold() for term in item["evidence"])
        points = 2 if evidence_hit and answer_correct else (1 if evidence_hit or doc_hit else 0)
        rubric_points += points
        print(f"Agent   : {agent_answer}")
        print(f"Agent có đủ ý: {'CÓ' if answer_correct else 'KHÔNG'} — điểm rubric: {points}/2")

    print("\n" + "=" * 88)
    print(f"Đúng doc_id trong Top-3 : {doc_hits}/5")
    print(f"Đủ bằng chứng trong Top-3: {evidence_hits}/5")
    print(f"ĐIỂM RETRIEVAL + AGENT  : {rubric_points}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
