import os
from openai import OpenAI

# 1. 初始化客户端
client = OpenAI(
    api_key="sk-***************************",  # 修改为自己的api key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 2. 定义 Function Calling 工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_markdown",
            "description": "读取 'documents' 文件夹中的 Markdown 文档。",
            "parameters": {
                "type": "object",
                "properties": {},  # 这个工具不需要参数
            },
        }
    }
]

def read_markdown():
    """
    读取 documents 文件夹中的首个 .md 文件，并返回前 2000 字符的内容。
    """
    doc_path = "documents"
    md_file = None

    for file in os.listdir(doc_path):
        if file.endswith(".md"):
            md_file = os.path.join(doc_path, file)
            break

    if not md_file:
        return "No markdown file found in the 'documents' folder."

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    return content[:2000]

def main():
    user_question = input("请输入问题：").strip()
    messages = [{"role": "user", "content": user_question}]

    # ============ 第一次请求：看看模型是否想调用工具 ============
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        tools=tools
    )

    #  **改成 .prompt_tokens`而不是 ["prompt_tokens"]
    total_prompt_tokens = completion.usage.prompt_tokens
    total_completion_tokens = completion.usage.completion_tokens
    total_tokens = completion.usage.total_tokens

    # 打印 JSON 便于调试
    print("=== 第一次请求结果（JSON）===")
    print(completion.model_dump_json())

    # 解析 Qwen 返回的 tool_calls
    first_answer = completion.to_dict()
    if not first_answer.get("choices"):
        print("[Info] 模型没有返回任何内容，结束。")
        return

    choice = first_answer["choices"][0]
    message = choice.get("message", {})
    tool_calls = message.get("tool_calls", [])

    if tool_calls:
        tool_results = []
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_id = tool_call["id"]
            tool_args = tool_call["function"]["arguments"]

            print(f"[Debug] 模型调用了工具: {tool_name}, call_id={tool_id}, args={tool_args}")

            if tool_name == "read_markdown":
                result_content = read_markdown()
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_id,  # 确保这里传入了 tool_call_id
                    "content": result_content
                })
            else:
                print(f"[Warning] 未知的工具调用: {tool_name}，跳过。")

        # 确保 tool 消息紧跟 assistant
        messages.append({
            "role": "assistant",
            "content": "",  # 重要！保持 assistant 为空，否则可能出错
            "tool_calls": tool_calls  # 这里保证调用工具的 assistant 消息完整
        })
        messages.extend(tool_results)  # 立即跟上工具的返回值

        # ============ 第二次请求：让模型读取工具结果，继续回答 ============
        completion2 = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            tools=tools
        )

        total_prompt_tokens += completion2.usage.prompt_tokens
        total_completion_tokens += completion2.usage.completion_tokens
        total_tokens += completion2.usage.total_tokens

        print("=== 第二次请求结果（JSON）===")
        print(completion2.model_dump_json())

        # 解析最终的回答
        second_answer = completion2.to_dict()
        if second_answer.get("choices"):
            final_content = second_answer["choices"][0].get("message", {}).get("content", "")
            print("\n【最终回答】", final_content)
        else:
            print("[Info] 第二次请求未获得任何回答。")

    else:
        # 如果没有调用工具，直接输出回答
        content = message.get("content", "")
        print("\n【模型回答】", content)

    #打印总 Token 消耗
    print("\n=== Token 消耗情况 ===")
    print(f"🔹 提示词 Token: {total_prompt_tokens}")
    print(f"🔹 生成内容 Token: {total_completion_tokens}")
    print(f"🔹 总 Token 消耗: {total_tokens}")

if __name__ == "__main__":
    main()
