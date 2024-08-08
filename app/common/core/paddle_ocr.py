# from paddleocr import PaddleOCR

# Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
# drop_score=0.99,得分阈值，小于此得分的文本框会被丢弃
# use_space_char=True,在中英文中是否使用空格分割
# use_angle_cls=True,使用文本方向分类的后处理方法
#  page_num=3,表示最多处理多少页，超过后不处理
ocr =' PaddleOCR(use_angle_cls=True, lang="ch", gpu_id=0, page_num=3)'


def img_to_text(img_path):
    '''Convert image to text using PaddleOCR

        Args:
        img_path (str): path to image file
    '''
    result = ocr.ocr(img_path, cls=True)
    text = ''
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            text += line[1][0] + ' '
    return text


def process_pdf(pdf_path):
    '''Process a PDF file and extract text from it

        Args:
        pdf_path (str): path to PDF file
    '''
    result = ocr.ocr(pdf_path, cls=True)
    text = ''
    for idx, res in enumerate(result):
        if res is None:  # Skip empty pages
            print(f"[DEBUG] Empty page {idx + 1} detected, skip it.")
            continue
        for line in res:
            text += line[1][0] + ' '
    return text.strip()
