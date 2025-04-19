import json
import os
import requests
import time
import threading
from datetime import datetime


def fetch_repos(api, model_name, languages, config_file='config.json', output_dir='out/api_repo'):
    """优化后的爬虫函数，确保每个范围由独立Token处理"""

    with open(config_file, 'r') as f:
        config = json.load(f)
    tokens = config['tokens']
    user_agent = config['user_agent']

    os.makedirs(output_dir, exist_ok=True)

    ranges = [
        (1, 14000), (14001, 28000), (28001, 42000),
        (42001, 56000), (56001, 70000), (70001, 84000),
        (84001, 98000), (98001, 112000), (112001, 126000),
        (126001, 140000), (140001, 154000), (154001, 168000),
        (168001, 182000), (182001, 196000), (196001, 210000)
    ]

    def save_progress(language, start, end, data):
        progress_file = os.path.join(
            os.path.join(output_dir, 'progress'),
            f"{model_name}_{language}_{start}_{end}_progress.json"
        )
        progress = {
            'start': start,
            'end': end,
            # 'data': data,
            'timestamp': str(datetime.now())
        }
        with open(progress_file, 'w') as f:
            json.dump(progress, f)

    def load_progress(language, start, end):
        progress_file = os.path.join(
            os.path.join(output_dir, 'progress'),
            f"{model_name}_{language}_{start}_{end}_progress.json"
        )
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return json.load(f)
        return None

    def crawl_language(language, token, start, end, data_store, lock):
        headers = {
            'Authorization': f'token {token}',
            'User-Agent': user_agent,
            'Accept': 'application/vnd.github.v3+json'
        }
        gap = 50
        current_start = start
        current_end = start + gap - 1

        progress = load_progress(language, start, end)
        if progress:
            current_start = progress['end'] + 1
            results = progress['data']
        else:
            results = []

        while current_end <= end:
            query = f"{api} in:file language:{language} size:{current_start}..{current_end}"
            page = 1
            print(f"处理 {language} | 范围 {current_start}-{current_end} | Token {tokens.index(token)}")

            while True:
                try:
                    url = f'https://api.github.com/search/code?q={query}&page={page}&per_page=100'
                    resp = requests.get(url, headers=headers, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                        results.extend(data.get('items', []))
                        with lock:
                            data_store.extend(data.get('items', []))
                        page += 1
                        if 'next' not in resp.links:
                            break
                    else:
                        print(f"错误码 {resp.status_code}，等待重试...")
                        time.sleep(30)
                except Exception as e:
                    print(f"请求异常: {e}")
                    time.sleep(15)
                time.sleep(2)

            save_progress(language, start, end, results)
            current_start += gap
            current_end += gap

    for lang in languages:
        print(f"\n========= 开始处理语言: {lang} =========")
        lang_data = []
        lock = threading.Lock()
        threads = []

        # 修改分配策略：每个range分配一个token，循环使用token列表
        for idx, (range_start, range_end) in enumerate(ranges):
            # 按顺序分配token
            token = tokens[idx % len(tokens)]
            t = threading.Thread(
                target=crawl_language,
                args=(lang, token, range_start, range_end, lang_data, lock)
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        output_path = os.path.join(output_dir, f"{model_name}_{lang}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, indent=2, ensure_ascii=False)
        print(f"已保存 {len(lang_data)} 条{lang}数据到 {output_path}")


if __name__ == '__main__':
    fetch_repos(
        api='api.openai.com',
        model_name='openai',
        languages=['Python', 'Java']
    )
