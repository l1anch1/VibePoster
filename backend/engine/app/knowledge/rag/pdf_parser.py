"""PDF 文本提取模块"""

from ...core.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    import pymupdf

    doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            pages.append(text)
    doc.close()

    if not pages:
        raise ValueError("PDF 文件无可提取的文本内容")

    result = "\n\n".join(pages)
    logger.info(f"PDF 解析完成: {len(pages)} 页, {len(result)} 字符")
    return result
