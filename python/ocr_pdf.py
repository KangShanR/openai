import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Windows 需要设置 Tesseract-OCR 安装路径（如果环境变量未配置）
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ocr_pdf(pdf_path, lang="chi_sim",start_page=1, max_pages=15):
    """ 读取 PDF 图片并进行 OCR 文字识别 """
    # 1. 将 PDF 转换为图片列表
    images = convert_from_path(pdf_path, first_page=start_page, last_page=max_pages)

    extracted_text = []
    for i, img in enumerate(images):
        # 2. 使用 Tesseract 进行 OCR 识别
        text = pytesseract.image_to_string(img, lang=lang)
        extracted_text.append(text)
        print(f"📄 解析第 {i+1} 页完成！")

    return "\n".join(extracted_text)

# 使用 OCR 识别 PDF
pdf_path = "/home/k/Documents/ebook/疯行天下-谢建光著-2016宁波出版社.pdf"  # 替换成你的 PDF 文件
text_result = ocr_pdf(pdf_path)

# 输出识别的文本
print("📝 识别文本如下：\n")
print(text_result)
