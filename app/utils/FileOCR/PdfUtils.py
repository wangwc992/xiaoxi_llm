import fitz  # PyMuPDF
import pandas as pd
import requests
from io import BytesIO
import tempfile
import os
from PIL import Image
import pytesseract

def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)

def extract_text_from_pdf(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_pdf_file:
        tmp_pdf_file.write(pdf_file.read())
        tmp_pdf_file_path = tmp_pdf_file.name
    doc = fitz.open(tmp_pdf_file_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # 尝试从页面中获取文本
        page_text = page.get_text()
        if page_text.strip():
            text += page_text
        else:
            # 图片型，使用模型或者OCR
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img = img.point(lambda x: 0 if x < 128 else 255)  # 二值化
            # 使用Tesseract进行OCR
            text += pytesseract.image_to_string(img, lang='chi_sim')  # 指定中文简体语言
    # 删除临时文件
    doc.close()  # 关闭文档
    os.remove(tmp_pdf_file_path)
    return text
def extract_text_from_excel(excel_file):
    xls = pd.ExcelFile(excel_file)
    text = ""
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name)
        text += df.to_string(index=False)
    return text

def main():
    #文字型
    #pdf_url = "https://xiaoxi-cdn.globeedu.com/2024/07/19/pdf/2024071915532394803013.pdf"  # 替换为你的PDF链接
    #图片型
    pdf_url = "https://xiaoxi-cdn.globeedu.com/2024/07/19/pdf/2024071915530687603013.pdf"  # 替换为你的PDF链接
    excel_url = "https://example.com/sample.xlsx"  # 替换为你的Excel链接

    # 处理PDF文件
    pdf_file = download_file(pdf_url)
    pdf_text = extract_text_from_pdf(pdf_file)
    print("PDF内容:\n", pdf_text)

    # 处理Excel文件
    # excel_file = download_file(excel_url)
    # excel_text = extract_text_from_excel(excel_file)
    # print("Excel内容:\n", excel_text)

if __name__ == "__main__":
    main()
