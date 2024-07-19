import requests
from io import BytesIO
from PIL import Image, ImageOps, ImageEnhance
import pytesseract

# 指定Tesseract的路径
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class OCRTester:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def load_image(self, file_path):
        return Image.open(file_path)
    def download_image(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))

    def preprocess_image(self, img):
        # 转为灰度图像
        img = ImageOps.grayscale(img)
        # 提高对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(5)
        # 调整图像大小，增加OCR识别率
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
        # 锐化图像
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2)
        # 反转颜色（黑白反转）
        img = ImageOps.invert(img)
        # 二值化
        img = img.point(lambda x: 0 if x < 128 else 255)
        return img

    def ocr_image(self, img, lang='chi_sim'):
        text = pytesseract.image_to_string(img, lang=lang)
        return text

    def process_image_url(self, url, lang='eng'):
        img = self.load_image(url)
        img = self.preprocess_image(img)
        text = self.ocr_image(img, lang)
        return text


def main():
    # 创建OCR测试实例
    ocr_tester = OCRTester()

    # 示例图片URL
    # image_url = "https://xiaoxi-cdn.globeedu.com/2023/04/27/jpg/2023042713503352903013.jpg"  # 替换为你的图片URL
    image_url = "D://123.png"  # 替换为你的图片URL

    # 处理图片并获取OCR结果
    ocr_text = ocr_tester.process_image_url(image_url, lang='chi_sim')  # 使用中文简体语言包
    print("OCR识别结果:\n", ocr_text)

if __name__ == "__main__":
    main()
