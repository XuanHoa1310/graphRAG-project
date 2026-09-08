# GraphRAG Project – Hệ thống hỏi đáp tài liệu sử dụng Local LLM

## 1. Giới thiệu

Đây là dự án nghiên cứu và xây dựng hệ thống hỏi đáp tài liệu dựa trên kiến trúc **GraphRAG**, kết hợp **Local Large Language Model (LLM)** với **Knowledge Graph** và **Vector Search**.

Mục tiêu của hệ thống là xây dựng một pipeline có khả năng:

- Đọc và xử lý tài liệu PDF/DOCX.
- Chia tài liệu thành các đoạn văn bản (chunks).
- Sử dụng Local LLM để trích xuất thực thể và quan hệ.
- Xây dựng Knowledge Graph từ thông tin được trích xuất.
- Kết hợp tìm kiếm vector và tìm kiếm trên đồ thị.
- Sử dụng Local LLM để tổng hợp ngữ cảnh và sinh câu trả lời.
- Cung cấp nguồn/citation giúp kiểm tra thông tin.

Hệ thống được định hướng chạy **local**, hạn chế phụ thuộc vào các API LLM bên ngoài.

---

## 2. Kiến trúc hệ thống

### 2.1. Indexing – Tạo đồ thị và vector

```text
PDF / DOCX
    │
    ▼
Document Parser
    │
    ▼
Section-aware Chunking
    │
    ▼
Qwen2.5-3B
Entity & Relation Extraction
    │
    ▼
Pydantic Schema Validation
    │
    ▼
Semantic Validation
    │
    ▼
Entity Resolution
    │
    ▼
NetworkX Knowledge Graph
    │
    ├──────────────► Graph Evaluation
    │
    ▼
Leiden Community Detection
    │
    ▼
Community Summarization
    │
    ▼
BGE-M3 Embedding
    │
    ▼
ChromaDB Vector Store

##  2.2. Query – Truy vấn và sinh câu trả lời
User Query
    │
    ▼
Query Entity Linking
    │
    ├──────────────► Vector Search
    │
    ├──────────────► Graph Search
    │
    └──────────────► Community Search
                         │
                         ▼
                  Context Fusion
                         │
                         ▼
                  Qwen2.5-3B
                  Generator Engine
                         │
                         ▼
              Final Answer + Sources
