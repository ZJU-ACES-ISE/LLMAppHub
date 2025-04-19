import json
import os
import requests
import time
import threading
from .ask_llm import get_model_name_from_llm
from pathlib import Path
def fetch_repos(api, model_name, languages, config_file = Path(__file__).parent / 'config.json', output_dir='out/api_repo/c1'):
    """
    抽象的爬取GitHub数据的函数，支持多个编程语言、API和大模型配置。

    :param api: GitHub API的URL。
    :param model_name: 大模型的名称，用于输出文件命名。
    :param languages: 支持的编程语言列表。
    :param config_file: 配置文件，包含token等信息，默认为config.json。
    :param output_dir: 输出文件夹，默认为out/api_repo。
    """

    # 从config.json读取token
    with open(config_file, 'r') as f:
        config = json.load(f)
    tokens = config['tokens']
    user_agent = config['user_agent']

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 如果目录不存在，创建目录

    target_records = []

    def crawl_language(language, token, start, end):
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': user_agent
        }
        results = []
        gap = 50
        current_start = start
        current_end = current_start + gap - 1
        while current_end <= end:
            # 修改查询参数：添加fork:false和stars:>0条件
            query = f"{api} in:file language:{language} fork:false size:{current_start}..{current_end}"
            page = 1
            print(
                f"正在爬取语言 {language}，文件大小范围 {current_start} 到 {current_end}，使用token索引 {tokens.index(token)}")
            while True:
                url = f'https://api.github.com/search/code?q={query}&per_page=100&page={page}'
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    results.extend(data.get('items', []))
                    target_records.extend(data.get('items', []))
                    if 'next' not in response.links:
                        break
                    page += 1
                else:
                    print(f'获取数据失败：{response.status_code}')
                    break
                time.sleep(10)  # 延迟以避免速率限制
            current_start += gap
            current_end += gap
            time.sleep(10)
        return results

    # 启动多线程爬取不同语言的代码
    try:
        threads = []
        ranges = [(1, 70000), (70001, 140000), (140001, 210000)]  # 可以根据需要调整爬取范围
        for language in languages:
            for i, token in enumerate(tokens):
                for start, end in ranges:
                    thread = threading.Thread(target=crawl_language, args=(language, token, start, end))
                    threads.append(thread)
                    thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()
    finally:
        # 保存结果到文件
        for language in languages:
            file_path = os.path.join(output_dir, f"{model_name}_{language}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(target_records, f, ensure_ascii=False, indent=4)
            print(f"共发现 {len(target_records)} 项数据，并已保存至 {file_path}")

# 定义新函数调用fetch_repos分别爬取不同语言
def fetch_repos_langs(api, model_name, languages=['Python', 'Java', 'JavaScript']):
    """
    爬取不同编程语言的代码库。

    :param api: GitHub API的URL。
    :param model_name: 大模型的名称，用于输出文件命名。
    :param languages: 支持的编程语言列表。
    """
    for language in languages:
        fetch_repos(api, model_name, [language])

if __name__ == '__main__':
    api = 'api.anthropic.com'
    model_name = get_model_name_from_llm(api)
    languages = ['PHP', 'GO']
    fetch_repos_langs(api, model_name, languages)