from pathlib import Path
import json
import re
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =========================
# CẤU HÌNH
# =========================

PROCESSED_DIR = Path("data/processed")
CHUNKS_DIR = Path("data/chunks")

# Tạo thư mục chunks nếu chưa tồn tại
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# TOKENIZER
# =========================

# Dùng tokenizer để đếm token
encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text):
    """Đếm số token bằng tiktoken."""
    return len(encoding.encode(text))


# =========================
# KIỂM TRA CHUNK RÁC
# =========================

def is_noise_chunk(text):
    """
    Kiểm tra chunk có phải là nội dung rác hay không.

    Chỉ loại bỏ:
    - Chuỗi rỗng
    - Chunk chỉ chứa số, ví dụ: "120"
    - Chunk không chứa chữ cái
    """

    text = text.strip()

    # Không có nội dung
    if not text:
        return True

    # Chỉ chứa số, ví dụ: "120", "101", "5"
    if re.fullmatch(r"\d+", text):
        return True

    # Không có chữ cái tiếng Việt hoặc tiếng Anh
    if not re.search(r"[A-Za-zÀ-ỹ]", text):
        return True

    return False


# =========================
# CHUNKER
# =========================

# Chunk tối đa 1000 token
# Overlap 100 token
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=count_tokens,
    separators=[
        "\n\n",
        "\n",
        ". ",
        ", ",
        " ",
        ""
    ]
)


# =========================
# TẠO CHUNKS
# =========================

def create_chunks(json_path):
    """Đọc một file JSON đã xử lý và tạo các chunk."""

    print(f"Đang xử lý: {json_path.name}")

    with open(json_path, "r", encoding="utf-8") as f:
        document = json.load(f)

    source_doc = document.get("filename", json_path.stem)

    all_chunks = []

    # Đếm số chunk bị loại
    removed_chunks = 0

    # Duyệt từng trang
    for page_data in document.get("pages", []):

        page_number = page_data.get("page")

        text = page_data.get("text", "").strip()

        if not text:
            continue

        # Tách text thành các chunk
        chunks = splitter.split_text(text)

        for i, chunk_text in enumerate(chunks):

            # =========================
            # LOẠI CHUNK RÁC
            # =========================

            if is_noise_chunk(chunk_text):

                removed_chunks += 1

                print(
                    f"  -> Bỏ chunk rác: "
                    f"trang {page_number} | "
                    f"nội dung: {repr(chunk_text)}"
                )

                continue

            # =========================
            # TẠO CHUNK ID
            # =========================

            chunk_id = (
                f"{json_path.stem}"
                f"_page_{page_number}"
                f"_chunk_{i + 1}"
            )

            # =========================
            # LƯU CHUNK
            # =========================

            chunk = {
                "chunk_id": chunk_id,
                "text": chunk_text,
                "source_doc": source_doc,
                "section": "",
                "page": page_number
            }

            all_chunks.append(chunk)

    # =========================
    # TÊN FILE OUTPUT
    # =========================

    output_path = CHUNKS_DIR / f"{json_path.stem}_chunks.json"

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(
            all_chunks,
            f,
            ensure_ascii=False,
            indent=2
        )

    # =========================
    # THỐNG KÊ
    # =========================

    print(f"  -> Tạo {len(all_chunks)} chunks")
    print(f"  -> Loại {removed_chunks} chunk rác")
    print(f"  -> Lưu: {output_path}")
    print()


# =========================
# MAIN
# =========================

def main():

    json_files = list(PROCESSED_DIR.glob("*.json"))

    if not json_files:

        print(
            "Không tìm thấy file JSON "
            "trong data/processed/"
        )

        print("Hãy kiểm tra lại bước ingestion.")

        return

    print(f"Tìm thấy {len(json_files)} file JSON.")

    print("Chunk size: 1000 token")
    print("Overlap: 100 token")
    print()

    for json_file in json_files:

        try:

            create_chunks(json_file)

        except Exception as e:

            print(
                f"LỖI khi xử lý "
                f"{json_file.name}: {e}"
            )

    print("================================")
    print("HOÀN THÀNH BƯỚC CHUNKING")
    print("================================")


# =========================
# CHẠY CHƯƠNG TRÌNH
# =========================

if __name__ == "__main__":
    main()