import logging
import time
import base64
import json
from pathlib import Path
from io import BytesIO

import pandas as pd
from PIL import Image
from openai import OpenAI

from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# === 运行配置 ===
ENABLE_OCR = True  # ✅ 一行控制：是否开启 OCR（RapidOCR）
DASHSCOPE_API_KEY = "sk-25073b1d5af2464292d41bfb04d92a7e"
VLM_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# === 路径配置 ===
input_pdf_path = Path("D:/Personal_Project/SmolDocling/pdfs/Gan.pdf")
output_dir = Path("D:/Personal_Project/SmolDocling/output2")
output_dir.mkdir(parents=True, exist_ok=True)
doc_filename = input_pdf_path.stem

# === 图像→base64→VLM接口 ===
def ask_image_vlm_base64(pil_image: Image.Image, prompt: str = "请描述这张图片") -> str:
    try:
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=VLM_API_URL)
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ]

        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[{"role": "user", "content": content}]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        log.warning(f"调用图像API失败: {e}")
        return "[图像描述失败]"

# === 主处理函数 ===
def convert_pdf_to_markdown_with_images():
    start_time = time.time()

    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = 2.0
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_table_images = True

    # ✅ 控制是否开启 OCR（使用 RapidOCR）
    if ENABLE_OCR:
        pipeline_options.do_ocr = True
        ocr_options = RapidOcrOptions(force_full_page_ocr=True)
        pipeline_options.ocr_options = ocr_options
    else:
        pipeline_options.do_ocr = False

    doc_converter = DocumentConverter(
        format_options={"pdf": PdfFormatOption(pipeline_options=pipeline_options)}
    )

    conv_res = doc_converter.convert(input_pdf_path)
    document = conv_res.document

    markdown_lines = []
    json_data = []

    table_counter = 0
    picture_counter = 0

    for element, level in document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            image_filename = output_dir / f"{doc_filename}-table-{table_counter}.png"
            table_df: pd.DataFrame = element.export_to_dataframe()
            element.get_image(document).save(image_filename, "PNG")

            markdown_lines.append(f"\n![Table {table_counter}](./{image_filename.name})\n")
            markdown_lines.append(table_df.to_markdown(index=False))
            markdown_lines.append("")

            json_data.append({
                "type": "table",
                "level": level,
                "image": image_filename.name,
                "data": table_df.to_dict(orient="records")
            })


        elif isinstance(element, PictureItem):
            picture_counter += 1
            image_filename = output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            pil_img = element.get_image(document)
            pil_img.save(image_filename, "PNG")
            caption = ask_image_vlm_base64(pil_img, prompt="请描述这张图中的内容，在一行中输出")
            markdown_lines.append(f"\n![Picture {picture_counter}](./{image_filename.name})\n")
            markdown_lines.append(f"<!-- 图像描述：{caption} -->\n")
            json_data.append({
                "type": "picture",
                "level": level,
                "image": image_filename.name,
                "caption": caption
            })

        else:
            if hasattr(element, "text") and element.text:
                text = element.text.strip()
                if text:
                    heading_prefix = "#" * min(level + 1, 6)
                    markdown_lines.append(f"{heading_prefix} {text}" if level <= 5 else text)
                    markdown_lines.append("")

                    json_data.append({
                        "type": "text",
                        "level": level,
                        "text": text
                    })

    # === 保存 Markdown
    markdown_file = output_dir / f"{doc_filename}.md"
    with markdown_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))

    # === 保存 JSON
    json_file = output_dir / f"{doc_filename}.json"
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    log.info(f"✅ PDF 转换完成，耗时 {elapsed:.2f} 秒")
    log.info(f"📄 Markdown 输出: {markdown_file.resolve()}")
    log.info(f"📦 JSON 输出: {json_file.resolve()}")


if __name__ == "__main__":
    convert_pdf_to_markdown_with_images()
