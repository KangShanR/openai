import os
import zipfile
import shutil
from bs4 import BeautifulSoup
from ebooklib import epub
import re

AD_PATTERNS = [
    r'微信(公)?众号.*?(推荐|关注|回复)',      # 包含“微信公众号推荐/关注/回复”等
    r'长按(二维码)?识别.*?(精彩|查看)',       # “长按识别二维码查看精彩内容”
    r'更多精彩内容.*?请.*?(扫码|点击|回复)',   # “更多精彩内容请扫码/点击/回复”
    r'免费下载.*?APP',                       # “免费下载XXX APP”
    r'阅读原文.*?获取',                       # “阅读原文获取全文”
    r'回复\s?\d{1,3}\s?获取.*?',             # “回复123获取”
    r'关注.*?公众号.*?',                     # “关注某某公众号”
    r'扫码.*?(关注|查看)',                   # “扫码查看/扫码关注”
    r'本书由.*?提供',                        # “本书由xxx提供”
    r'广告[：:]?.*',                          # 开头“广告：xxx”
    r'\[.+shu\]',
]

# 要删除的广告关键词，可以按需扩充
AD_KEYWORDS = [
    "关注微信公众号", "免费下载", "广告", "推广", "长按识别", "更多精彩", "回复数字", "微信扫一扫", "扫码阅读"
]

def remove_ads_from_html(html_content):
    soup = BeautifulSoup(html_content, "lxml")

    # 遍历所有文本标签
    for tag in soup.find_all(["p", "div", "span"]):
        text = tag.get_text().strip()
        # 如果正则匹配任何广告语句，就删除整个标签
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in AD_PATTERNS):
            print(f"删除广告内容：{text}")
            tag.string = ""

    return str(soup)

def clean_epub(input_path, output_path):
    # 创建临时目录解压
    temp_dir = "temp_epub"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)

    # 解压 epub 文件
    with zipfile.ZipFile(input_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 遍历 html/xhtml 文件并清理广告
    for root, _, files in os.walk(temp_dir):
        for file in files:
            if file.endswith((".xhtml", ".html")):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                cleaned_content = remove_ads_from_html(content)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)

    # 压缩回 epub
    with zipfile.ZipFile(output_path, 'w') as new_epub:
        for foldername, subfolders, filenames in os.walk(temp_dir):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, temp_dir)
                new_epub.write(filepath, arcname)

    shutil.rmtree(temp_dir)
    print(f"已生成干净版本：{output_path}")

# 示例使用
clean_epub("原文件.epub", "干净版.epub")
