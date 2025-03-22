from paddleocr import PaddleOCR
from pdf2image import convert_from_path

def ocr_pdf_paddle(pdf_path, start_page=1, max_page=5, use_gpu=False):
    """使用 PaddleOCR 识别 PDF 前 max_pages 页的文字"""
    
    # 初始化 PaddleOCR，指定语言为中文（ch），自动模式
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=use_gpu)

    # 只转换前 max_pages 页
    images = convert_from_path(pdf_path, first_page=start_page, last_page=max_page)

    extracted_text = []
    for i, img in enumerate(images):
        # 进行 OCR 识别
        result = ocr.ocr(img, cls=True)

        # 提取文本内容
        text_per_page = []
        for line in result:
            for word_info in line:
                text_per_page.append(word_info[1][0])  # 获取识别出的文字部分
        
        extracted_text.append("\n".join(text_per_page))
        print(f"📄 解析第 {i+1} 页完成！")

    return "\n".join(extracted_text)

# 运行 OCR 识别前 5 页
pdf_path = "/home/k/Documents/ebook/疯行天下-谢建光著-2016宁波出版社.pdf"  # 替换为你的 PDF 文件路径
text_result = ocr_pdf_paddle(pdf_path,start_page=1, max_page=8)

# 输出识别文本
print("📝 识别文本如下：\n")
print(text_result)
