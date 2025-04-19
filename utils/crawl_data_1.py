import json
import os
import requests
import time
import threading
from datetime import datetime


def fetch_repos(api, model_name, languages, config_file='config.json', output_dir='out/api_repo'):
    """
    抽象地爬取GitHub数据的函数，支持多个编程语言、API和大模型配置。
    优化了状态持久化、线程管理和网络波动的处理。
    """

    # 从config.json读取token
    with open(config_file, 'r') as f:
        config = json.load(f)
    tokens = config['tokens']
    user_agent = config['user_agent']

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 如果目录不存在，创建目录

    target_records = []

    # 加载历史进度文件
    def load_progress(language, model_name):
        progress_file = os.path.join(output_dir, f"{model_name}_{language}_progress.json")
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return json.load(f)
        return None

    def save_progress(language, model_name, start, end, data):
        progress = {
            'start': start,
            'end': end,
            'data': data,
            'timestamp': str(datetime.now())
        }
        progress_file = os.path.join(output_dir, f"{model_name}_{language}_progress.json")
        with open(progress_file, 'w') as f:
            json.dump(progress, f)

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

        # 检查是否有历史进度
        progress = load_progress(language, model_name)
        if progress and progress['end'] > current_start:
            current_start = progress['end'] + 1
            results = progress['data']

        while current_end <= end:
            query = f"{api} in:file language:{language} size:{current_start}..{current_end}"
            page = 1
            print(
                f"正在爬取语言 {language}，文件大小范围 {current_start} 到 {current_end}，使用token索引 {tokens.index(token)}")
            while True:
                try:
                    url = f'https://api.github.com/search/code?q={query}&per_page=100&page={page}'
                    response = requests.get(url, headers=headers, timeout=30)  # 设置超时
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
                except requests.exceptions.RequestException as e:
                    print(f"请求失败: {e}，正在重试...")
                    time.sleep(10)
                    continue
                time.sleep(5)  # 调整延迟
            current_start += gap
            current_end += gap

            # 定期保存进度
            save_progress(language, model_name, current_start, current_end, results)

        return results

    # 启动多线程爬取不同语言的代码
    try:
        threads = []
        # ranges = [(1, 70000), (70001, 140000), (140001, 210000)]  # 可以根据需要调整爬取范围
        ranges = [
            (1, 14000),  # 第一个区间
            (14001, 28000),  # 第二个区间
            (28001, 42000),  # 第三个区间
            (42001, 56000),  # 第四个区间
            (56001, 70000),  # 第五个区间
            (70001, 84000),  # 第六个区间
            (84001, 98000),  # 第七个区间
            (98001, 112000),  # 第八个区间
            (112001, 126000),  # 第九个区间
            (126001, 140000),  # 第十个区间
            (140001, 154000),  # 第十一个区间
            (154001, 168000),  # 第十二个区间
            (168001, 182000),  # 第十三个区间
            (182001, 196000),  # 第十四个区间
            (196001, 210000)  # 第十五个区间
        ]
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

if __name__ == '__main__':
    # api = 'suggested_questions_after_answer'
    # model_name = 'dify'
    # languages = ['YAML']
    # fetch_repos(api, model_name, languages)

    api = 'api.openai.com'
    model_name = 'openai'
    languages = ['Python','Java','JavaScript']
    fetch_repos(api, model_name, languages)