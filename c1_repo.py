import os
import json
from typing import List, Dict

def process_repos(input_folder: str, output_folder: str):
    """
    处理JSON文件并提取所需信息
    :param input_folder: 输入文件夹路径
    :param output_folder: 输出文件夹路径
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith('.json'):
            continue

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"repo_{filename}")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                original_data: List[Dict] = json.load(f)

            seen = set()
            processed_data = []

            for item in original_data:
                # 安全提取 repository 信息
                repo = item.get("repository")
                if not repo:
                    continue

                # 通过 full_name 去重
                full_name = repo.get("full_name")
                if not full_name or full_name in seen:
                    continue
                seen.add(full_name)

                # 构建精简数据结构
                processed_data.append({
                    "full_name": full_name,
                    "name": repo.get("name"),
                    # "owner": repo.get("owner"),
                    "description": repo.get("description"),
                })

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
                print(f"已处理 {filename} | 有效条目：{len(processed_data)}")

        except Exception as e:
            print(f"处理 {filename} 失败: {str(e)}")

if __name__ == "__main__":
    input_dir = "out/api_repo/c1_with_framework_keywords"
    output_dir = "out/api_repo/c1_repo_owner_des"
    process_repos(input_dir, output_dir)
