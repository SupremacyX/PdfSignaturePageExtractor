import fitz  # PyMuPDF
import os
import re
import argparse
from pathlib import Path

def extract_company_line_text(page):
   
    text_dict = page.get_text("dict")
    previous_line_text = ""
    
    for block in text_dict["blocks"]:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            spans = line.get("spans", [])
            # print(f"spans: {spans}")
            if not spans:
                continue
                
            # Get current line text
            current_line_text = "".join(span["text"] for span in spans).strip()
            
            # Check if current line is "(盖章)"
            if (current_line_text == "(盖章)" or current_line_text == "（盖章）") and previous_line_text:
                return previous_line_text
                
            # Store current line text for next iteration
            previous_line_text = current_line_text
            
    return ""

def sanitize_filename(name):
    """
    处理文件名，将非法字符去掉，只保留字母、数字、空格、下划线和短横线
    """
    name = name.strip()
    # 替换连续空白字符为单个下划线
    name = re.sub(r"\s+", "_", name)
    # 去除非允许字符
    return "".join(c for c in name if c.isalnum() or c in ("_", "-"))

def extract_last_signature_name(page):
    """
    提取最后一个"签署"相关行之前的第一个非空行文本
    """
    text_dict = page.get_text("dict")
    lines = []
    
    # 收集所有行的文本
    for block in text_dict["blocks"]:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            text = "".join(span["text"] for span in line.get("spans", [])).strip()
            if text:
                lines.append(text)
    
    # 从后向前查找包含"签署"的行
    signature_index = -1
    for i in range(len(lines) - 1, -1, -1):
        if "签署" in lines[i]:
            signature_index = i
            break
    
    # 如果找到签署行，向前查找第一个非空行
    if signature_index > 0:
        for i in range(signature_index - 1, -1, -1):
            if lines[i] and lines[i] not in ["（盖章）", "(盖章)"]:
                return lines[i]
    
    return ""

def split_pdf_by_page(pdf_path, start_page, end_page, output_dir):
    """
    读取 pdf_path 文件，对 start_page 到 end_page 的页面进行拆分，
    每页生成一个新的 PDF 文件，文件名为该页第一个整行粗体文本（如果没有找到，则尝试其他方式）。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    if start_page < 1 or end_page > total_pages or start_page > end_page:
        print("页码范围不合法！")
        return

    for i in range(start_page - 1, end_page):
        page = doc.load_page(i)
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

        # 首先尝试提取公司名
        filename_text = extract_company_line_text(page)
        
        # 如果没有找到公司名，尝试提取签署相关人名
        if not filename_text:
            filename_text = extract_last_signature_name(page)
            
        # 如果两种方法都没找到，使用默认名称
        if not filename_text:
            filename_text = f"page_{i+1}"
            
        # 处理文件名中的非法字符
        valid_filename = sanitize_filename(filename_text)
        if not valid_filename:
            valid_filename = f"page_{i+1}"
            
        output_file = os.path.join(output_dir, f"{valid_filename}.pdf")
        new_doc.save(output_file)
        new_doc.close()
        print(f"已生成: {output_file}")

    doc.close()

if __name__ == "__main__":
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='PDF文件签名页提取工具')
    
    # 添加命令行参数
    parser.add_argument('pdf_path', type=str, help='输入PDF文件路径')
    parser.add_argument('--start', type=int, default=1, help='起始页码（从1开始，默认为1）')
    parser.add_argument('--end', type=int, help='结束页码（默认为PDF最后一页）')
    parser.add_argument('--output', type=str, default='output', help='输出目录路径（默认为output）')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 验证输入文件是否存在
    if not os.path.exists(args.pdf_path):
        print(f"错误：输入文件 '{args.pdf_path}' 不存在")
        exit(1)
    
    # 如果没有指定结束页码，则获取PDF总页数
    if args.end is None:
        with fitz.open(args.pdf_path) as doc:
            args.end = doc.page_count
    
    # 调用处理函数
    split_pdf_by_page(args.pdf_path, args.start, args.end, args.output)
