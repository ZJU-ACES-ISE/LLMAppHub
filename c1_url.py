# 筛选包含框架相关的关键词
import os
import json
import shutil
from typing import List, Dict
from fuzzywuzzy import fuzz
from utils import crawl_data

framework_keywords = [
        "framework", "library", "sdk", "toolkit", "platform",
        "llm", "gpt", "finetune", "agent", "rag",
        "middleware", "pipeline", "workflow", "orchestration",
        "prompt engineering", "model serving", "inference"
    ]
# 筛选函数, 通过关键词模糊过滤
def fuzzy_match(text: str, keyword: str, threshold: int = 70) -> bool:
    """
    执行模糊匹配的辅助函数
    :param text: 待匹配文本
    :param keyword: 目标关键词
    :param threshold: 相似度阈值(0-100)
    """
    # 同时尝试两种匹配策略
    return (
            fuzz.partial_ratio(text, keyword) >= threshold or  # 部分字符串匹配
            fuzz.token_sort_ratio(text, keyword) >= threshold  # 忽略词序匹配
    )


def filter_repos(data: List[Dict], keywords: List[str], fuzzy_threshold: int = 65) -> List[Dict]:
    """
    增强版过滤函数，支持模糊匹配
    """
    filtered = []
    preprocessed_keywords = [k.lower().strip() for k in keywords]

    for item in data:
        repo = item.get("repository")
        if not repo:
            continue

        # 准备匹配文本（合并名称和描述）
        name = str(repo.get("name") or "").lower()
        desc = str(repo.get("description") or "").lower()
        full_text = f"{name} {desc}"

        # 修改变量名避免冲突（关键修复）
        has_exact_match = any(
            keyword in name or keyword in desc
            for keyword in preprocessed_keywords
        )

        # 将变量名从 fuzzy_match 改为 has_fuzzy_match
        has_fuzzy_match = any(
            fuzzy_match(full_text, keyword, fuzzy_threshold)
            for keyword in preprocessed_keywords
        )

        if has_exact_match or has_fuzzy_match:  # 使用修改后的变量名
            filtered.append(item)

    return filtered

def filter_files(
        input_folder: str ='out/api_repo/c1',
        output_folder: str = 'out/api_repo/c1_with_framework_keywords',
        keywords: List[str] = framework_keywords,
        fuzzy_threshold: int = 65  # 添加可配置参数
):
    """
    处理文件时增加模糊阈值参数
    """
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith('.json'):
            continue

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"with_kw_{filename}")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)

            filtered_data = filter_repos(
                original_data,
                keywords,
                fuzzy_threshold=fuzzy_threshold
            )

            if filtered_data:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(filtered_data, f, ensure_ascii=False, indent=2)
                    print(f"已保存模糊过滤结果：{output_path}")
            else:
                print(f"文件 {filename} 无匹配（含模糊匹配）")

        except Exception as e:
            print(f"处理 {filename} 出错: {str(e)}")


def collect_api_data(api_url: str, model_name: str, languages: List[str]):
    """
    1. 调用 fetch_repos_langs 获取指定 API、模型和语言的仓库数据
    2. 将结果写入 out/api_repo/c1 文件夹
    3. 调用本模块的 filter_files 函数进行关键词过滤
    """
    # 第一步：获取数据
    crawl_data.fetch_repos_langs(api_url, model_name, languages)

    # 第二步：过滤原始数据
    filter_files()

# 示例
#if __name__ == "__main__":
    # 直接输入API URL
    # user_input = input("直接输入api: ")
    # search_api = user_input

    # 输入框架名称，llm返回对应的API URL
    # user_input = input("输入大模型名称: ")
    # search_api = get_url_from_llm(user_input)
    # print(f"Using API URL: {search_api}")

    # 设置输入和输出文件夹路径
    # input_folder = 'out/api_repo/filter_repo_cutfork_c1'
    # input_folder = 'out/api_repo/c1'
    # output_folder = 'out/api_repo/c1_with_framework_keywords'
    #
    # # 关键词列表
    # framework_keywords = [
    #     "framework", "library", "sdk", "toolkit", "platform",
    #     "llm", "gpt", "finetune", "agent", "rag",
    #     "middleware", "pipeline", "workflow", "orchestration",
    #     "prompt engineering", "model serving", "inference"
    # ]


    # 先爬取数据
    # 调用函数处理文件
    # 调用utils文件夹内的crawl_data.py中的fetch_repos函数
