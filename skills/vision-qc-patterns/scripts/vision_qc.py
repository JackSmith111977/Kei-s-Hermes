#!/usr/bin/env python3
"""
PDF 视觉质检独立脚本 (Vision QC)
用法：
  python3 vision_qc.py --pdf /path/to/output.pdf
  python3 vision_qc.py --pdf /path/to/output.pdf --sample all
  python3 vision_qc.py --pdf /path/to/output.pdf --sample key
  python3 vision_qc.py --pdf /path/to/output.pdf --pages 1,3,5
"""
import subprocess, sys, argparse, os, json

def get_page_count(pdf_path):
    """获取 PDF 总页数"""
    result = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True)
    for line in result.stdout.split("\n"):
        if line.strip().startswith("Pages:"):
            return int(line.split(":")[1].strip())
    return 1

def extract_page(pdf_path, page_num, output_dir="/tmp", dpi=150):
    """将指定页转为 PNG"""
    prefix = f"{output_dir}/qc_page"
    result = subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi),
         "-f", str(page_num), "-l", str(page_num),
         pdf_path, prefix],
        capture_output=True, text=True
    )
    png_path = f"{prefix}-{page_num}.png"
    if os.path.exists(png_path):
        return png_path
    return None

def select_pages(total, strategy="key"):
    """根据策略选择要检查的页"""
    if strategy == "all":
        return list(range(1, total + 1))
    elif strategy == "first":
        return [1]
    elif strategy == "key":
        pages = [1]  # 首页必查
        if total > 1:
            pages.append(total)  # 最后一页
        if total > 2:
            pages.append(total // 2 + 1)  # 中间页
        if total > 4:
            pages.append(3)  # 第3页
        return sorted(set(pages))
    else:
        return [1]

def generate_qc_report(png_paths, pdf_path):
    """生成质检报告（供 vision_analyze 使用）"""
    print("\n=== PDF 视觉质检报告 ===")
    print(f"PDF 文件: {pdf_path}")
    print(f"检查页数: {len(png_paths)} 页")
    print()

    for i, png_path in enumerate(png_paths):
        page_num = i + 1
        file_size = os.path.getsize(png_path)
        print(f"第 {page_num} 页: {png_path} ({file_size/1024:.1f} KB)")

    print("\n请将以上图片路径传入 vision_analyze 进行视觉检查")
    print("推荐 Prompt：")
    print("""
请检查以下 PDF 页面预览图，按以下错误模式逐一排查：
1. 文字粘连：行间距是否正常？
2. 方块字：中文是否显示为□□□？
3. 内容截断：表格/代码块是否被切断？
4. 表格异常：边框、背景色是否正常？
5. 对齐问题：标题、正文缩进是否一致？
6. 页码：页码是否连续正确？
    """)

    # 输出 JSON 格式供程序化使用
    report = {
        "pdf": pdf_path,
        "pages_checked": len(png_paths),
        "images": png_paths
    }
    report_path = "/tmp/vision_qc_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nJSON 报告已保存: {report_path}")
    return report

def main():
    parser = argparse.ArgumentParser(description="PDF 视觉质检工具")
    parser.add_argument("--pdf", required=True, help="PDF 文件路径")
    parser.add_argument("--sample", default="key", choices=["all", "key", "first"],
                       help="抽样策略: all=全部, key=关键页, first=仅首页")
    parser.add_argument("--pages", help="指定页码，逗号分隔 (如 1,3,5)")
    parser.add_argument("--dpi", type=int, default=150, help="预览图 DPI (默认150)")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"错误: 文件不存在 {args.pdf}")
        sys.exit(1)

    total = get_page_count(args.pdf)
    print(f"PDF 总页数: {total}")

    if args.pages:
        page_list = [int(p) for p in args.pages.split(",")]
    else:
        page_list = select_pages(total, args.sample)

    print(f"将检查页码: {page_list}")

    png_paths = []
    for page in page_list:
        png = extract_page(args.pdf, page, dpi=args.dpi)
        if png:
            png_paths.append(png)
            print(f"  ✅ 第 {page} 页 → {png}")
        else:
            print(f"  ❌ 第 {page} 页提取失败")

    if png_paths:
        generate_qc_report(png_paths, args.pdf)
    else:
        print("错误: 没有成功提取任何页面")
        sys.exit(1)

if __name__ == "__main__":
    main()
