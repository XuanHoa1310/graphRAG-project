from pathlib import Path
import json
import statistics
import fitz


# ============================================================
# CẤU HÌNH
# ============================================================

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# KHÔI PHỤC KHOẢNG TRẮNG DỰA TRÊN TỌA ĐỘ PDF
# ============================================================

def reconstruct_line(chars):
    """
    Khôi phục khoảng trắng giữa các từ dựa trên khoảng cách
    tọa độ X giữa các ký tự trong PDF.

    Không sử dụng dictionary.
    """

    if not chars:
        return ""

    # Sắp xếp ký tự từ trái sang phải
    chars = sorted(chars, key=lambda c: c["bbox"][0])

    # Lấy kích thước font trung vị
    font_sizes = [
        c.get("size", 10)
        for c in chars
        if c.get("size")
    ]

    if font_sizes:
        font_size = statistics.median(font_sizes)
    else:
        font_size = 10

    # Ngưỡng xác định khoảng trắng
    threshold = max(1.5, font_size * 0.20)

    result = []

    for i, char in enumerate(chars):

        result.append(char["c"])

        # Ký tự cuối dòng
        if i == len(chars) - 1:
            continue

        current_x1 = char["bbox"][2]
        next_x0 = chars[i + 1]["bbox"][0]

        gap = next_x0 - current_x1

        # Nếu khoảng cách đủ lớn -> thêm khoảng trắng
        if gap > threshold:
            result.append(" ")

    return "".join(result)


# ============================================================
# LÀM SẠCH TEXT
# ============================================================

def clean_text(text):
    """
    Chuẩn hóa text sau khi khôi phục khoảng trắng.
    """

    if not text:
        return ""

    # Chuẩn hóa xuống dòng
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.split("\n"):

        # Loại bỏ khoảng trắng thừa
        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines)


# ============================================================
# TRÍCH XUẤT MỘT TRANG PDF
# ============================================================

def extract_page_text(page):
    """
    Trích xuất text từ một trang PDF bằng rawdict.

    Mỗi ký tự có tọa độ bbox.
    Dựa vào khoảng cách giữa các ký tự để
    tự động khôi phục khoảng trắng.
    """

    data = page.get_text("rawdict", sort=True)

    lines_result = []

    for block in data.get("blocks", []):

        # Block hình ảnh thường không có lines
        if "lines" not in block:
            continue

        for line in block["lines"]:

            chars = []

            for span in line.get("spans", []):

                font_size = span.get("size", 10)

                for char in span.get("chars", []):

                    character = char.get("c", "")

                    if not character:
                        continue

                    chars.append({
                        "c": character,
                        "bbox": char["bbox"],
                        "size": font_size
                    })

            if chars:

                line_text = reconstruct_line(chars)

                line_text = line_text.strip()

                if line_text:
                    lines_result.append(line_text)

    return clean_text("\n".join(lines_result))


# ============================================================
# XỬ LÝ MỘT FILE PDF
# ============================================================

def process_pdf(pdf_path):

    print("=" * 70)
    print(f"Đang xử lý: {pdf_path.name}")
    print("=" * 70)

    try:

        doc = fitz.open(pdf_path)

        pages = []

        for page_index in range(len(doc)):

            page_number = page_index + 1

            page = doc[page_index]

            print(
                f"  Đang xử lý trang "
                f"{page_number}/{len(doc)}",
                end="\r"
            )

            text = extract_page_text(page)

            pages.append({
                "page": page_number,
                "text": text
            })

        doc.close()

        # Tạo document JSON
        document = {
            "filename": pdf_path.name,
            "num_pages": len(pages),
            "pages": pages
        }

        # Đường dẫn output
        output_path = PROCESSED_DIR / f"{pdf_path.stem}.json"

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                document,
                f,
                ensure_ascii=False,
                indent=2
            )

        print()
        print(f"  -> {len(pages)} trang")
        print(f"  -> Đã lưu: {output_path}")
        print()

        return True

    except Exception as e:

        print()
        print(f"  !!! LỖI: {e}")
        print()

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("PDF INGESTION - COORDINATE BASED EXTRACTION")
    print("=" * 70)
    print()

    pdf_files = list(RAW_DIR.glob("*.pdf"))

    if not pdf_files:

        print(
            "Không tìm thấy file PDF trong "
            "data/raw/"
        )

        return

    print(
        f"Tìm thấy {len(pdf_files)} file PDF."
    )

    print()

    success = 0
    failed = 0

    for pdf_path in pdf_files:

        result = process_pdf(pdf_path)

        if result:
            success += 1
        else:
            failed += 1

    print("=" * 70)
    print("HOÀN THÀNH INGESTION")
    print("=" * 70)

    print(f"Thành công : {success}")
    print(f"Lỗi        : {failed}")
    print(f"Output     : {PROCESSED_DIR}")

    print()


# ============================================================
# CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":
    main()