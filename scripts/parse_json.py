import json

def auto_parse_json(obj):
    """递归解析嵌套的 JSON 字符串"""
    if isinstance(obj, dict):
        return {k: auto_parse_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [auto_parse_json(item) for item in obj]
    elif isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            return auto_parse_json(parsed)  # 递归处理解析后的内容
        except (json.JSONDecodeError, TypeError):
            return obj  # 不是 JSON 字符串，原样返回
    else:
        return obj


# 1. 读取原始 JSON 文件
input_file = "data/character_v5.json"
output_file = "data/character_v5_2.json"

with open(input_file, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# 2. 自动解析嵌套 JSON 字符串
clean_data = auto_parse_json(raw_data)

# 3. 保存为格式化的新 JSON 文件
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(clean_data, f, ensure_ascii=False, indent=4)

print(f"✅ 已保存解析后的数据到 {output_file}")
