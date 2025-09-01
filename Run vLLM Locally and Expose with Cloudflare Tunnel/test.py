import os
import base64
from openai import OpenAI

# --- 配置 ---
MODEL_IDENTIFIER = "Qwen/Qwen2.5-VL-7B-Instruct"
API_BASE_URL = "http://localhost:8001/v1" #本地测试
# API_BASE_URL = "https://qwen-vl.你的域名/v1" #公网测试
TEST_IMAGE_PATH = "test_image.jpg" # 确保此图片与脚本在同一目录下

# 初始化 OpenAI 客户端，指向本地 vLLM 服务器
client = OpenAI(
    api_key="not-needed-for-local-deployment",
    base_url=API_BASE_URL,
)

def encode_image_to_base64(image_path):
    """将本地图片文件编码为 Base64 字符串"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"错误：测试图片未找到，请在目录下放置一张名为 '{image_path}' 的图片。")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_vision_and_text_task():
    """测试多模态能力：理解图片并回答问题"""
    print("\n--- 任务 1: 图片理解测试 ---")
    try:
        base64_image = encode_image_to_base64(TEST_IMAGE_PATH)
        print(f"成功加载并编码图片: {TEST_IMAGE_PATH}")

        response = client.chat.completions.create(
            model=MODEL_IDENTIFIER,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请详细描述这张图片的内容。"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
            temperature=0.7,
        )
        print("模型回答:")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"图片理解任务失败: {e}")

def test_pure_text_task():
    """测试纯文本对话能力"""
    print("\n--- 任务 2: 纯文本对话测试 ---")
    try:
        response = client.chat.completions.create(
            model=MODEL_IDENTIFIER,
            messages=[
                {"role": "system", "content": "你是一个乐于助人的人工智能助手。"},
                {"role": "user", "content": "你好，请给我介绍一下什么是大型语言模型？"},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        print("模型回答:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"纯文本对话任务失败: {e}")

if __name__ == "__main__":
    # 执行图片理解测试
    test_vision_and_text_task()

    # 执行纯文本对话测试
    test_pure_text_task()
