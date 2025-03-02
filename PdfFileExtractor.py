from pikepdf import Pdf
import fitz  # PyMuPDF
import os
import re

def extract_bold_text(pdf_path, page_num):
    """提取页面中第一个连续的粗体文本字符串"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    print(f"\n=== 第 {page_num + 1} 页分析 ===")
    
    # 获取页面文本信息
    blocks = page.get_text("dict")["blocks"]
    
    # 收集字体信息
    fonts = set()
    bold_text = ""
    found_bold = False
    
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                font_name = span["font"]
                fonts.add(font_name)
                text = span["text"]
                print(f"文本: {text}, 字体: {font_name}, 字重: {span.get('flags', 0)}")
                print(f"span info: {span}")
                # 检查是否是粗体
                is_bold = (
                    "bold" in font_name.lower() 
                    # "heavy" in font_name.lower() or
                    # "black" in font_name.lower() or
                    # "粗体" in font_name or
                    # "黑体" in font_name or
                    # (span.get("flags", 0) & 2**2) != 0  # 检查字体标志位
                )
                
                if is_bold and text.strip():
                    print(f"找到粗体文本: {text}")
                    if not found_bold:
                        found_bold = True
                        bold_text = text
                    else:
                        bold_text += ' ' + text
                elif found_bold:
                    doc.close()
                    return bold_text.strip()
    
    print(f"页面包含的字体: {fonts}")
    doc.close()
    return bold_text.strip()

def split_pdf_by_page(pdf_path, start_page, end_page, output_dir):
    """读取 pdf_path 文件并按页拆分"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with Pdf.open(pdf_path) as doc:
        total_pages = len(doc.pages)
        
        # 检查页码范围合法性
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            print("页码范围不合法！")
            return

        for i in range(start_page - 1, end_page):
            # 创建新的 PDF 文件
            new_pdf = Pdf.new()
            new_pdf.pages.append(doc.pages[i])
            
            # 提取粗体文本作为文件名
            bold_text = extract_bold_text(pdf_path, i)
            valid_filename = bold_text if bold_text else f"page_{i+1}"
            # 处理文件名中的非法字符
            valid_filename = re.sub(r'\s+', '_', valid_filename)
            valid_filename = re.sub(r'[\\/*?:"<>|]', '', valid_filename)
            
            output_file = os.path.join(output_dir, f"{valid_filename}.pdf")
            new_pdf.save(output_file)
            print(f"已生成: {output_file}")

if __name__ == "__main__":
    pdf_path = "test_file.pdf"          # 输入PDF路径
    start_page = 4         # 指定起始页（从 1 开始计数）
    end_page = 9           # 指定结束页
    output_dir = "output"  # 输出目录

    split_pdf_by_page(pdf_path, start_page, end_page, output_dir)