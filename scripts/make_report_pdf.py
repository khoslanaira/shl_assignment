from pathlib import Path
import textwrap


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "report_summary.md"
TARGET = ROOT / "submission_summary.pdf"


def pdf_escape(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_markdown(text):
    lines = []
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            lines.append("")
            continue
        if raw.startswith("# "):
            lines.append(raw[2:].upper())
            lines.append("")
        elif raw.startswith("## "):
            lines.append(raw[3:])
        else:
            lines.extend(textwrap.wrap(raw, width=92))
    return lines


def build_page(lines, page_number):
    y = 760
    commands = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
    for line in lines:
        commands.append(f"({pdf_escape(line)}) Tj")
        commands.append("T*")
        y -= 14
    commands.append(f"({pdf_escape('Page ' + str(page_number))}) Tj")
    commands.append("ET")
    return "\n".join(commands).encode("ascii")


def write_pdf(pages):
    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii"))
    for i, page in enumerate(pages):
        content_id = 4 + i * 2
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            f"/Contents {content_id} 0 R >>".encode("ascii")
        )
        objects.append(b"<< /Length " + str(len(page)).encode("ascii") + b" >>\nstream\n" + page + b"\nendstream")

    output = [b"%PDF-1.4\n"]
    offsets = []
    for idx, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part) for part in output))
        output.append(f"{idx} 0 obj\n".encode("ascii"))
        output.append(obj)
        output.append(b"\nendobj\n")

    xref = sum(len(part) for part in output)
    output.append(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.append(b"0000000000 65535 f \n")
    for offset in offsets:
        output.append(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.append(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    TARGET.write_bytes(b"".join(output))


def main():
    lines = wrap_markdown(SOURCE.read_text(encoding="utf-8"))
    page_lines = [lines[:46], lines[46:92]]
    pages = [build_page(page, i + 1) for i, page in enumerate(page_lines) if page]
    if len(pages) > 2:
        raise SystemExit("Report is longer than two pages.")
    write_pdf(pages)
    print(TARGET)


if __name__ == "__main__":
    main()
