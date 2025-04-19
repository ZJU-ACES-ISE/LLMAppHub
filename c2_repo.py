from utils.crawl_data import fetch_repos
from utils.ask_llm import get_repo_from_llm
import subprocess


def get_dependents(repo: str, output_file: str):
    # 构造命令行，直接将输出文件作为命令的一部分
    command = [
        'github-dependents-info',
        '--repo', repo,
        '-p',
        '-j',
        '--sort', 'stars',
        '--verbose',
        '>', output_file
    ]

    result = subprocess.run(' '.join(command), shell=True, stderr=subprocess.PIPE, text=True)

    if result.stderr:
        print(result.stderr)
    else:
        print(f"Dependents data saved to {output_file}")


# 示例
if __name__ == "__main__":
    # # 直接输入repo，格式为 owner/repo
    # user_input = input("直接输入repo: ")
    # search_api = user_input

    # 输入框架名称，llm返回对应的API URL
    # user_input = input("输入大模型名称: ")
    # search_api = get_repo_from_llm(user_input)
    # print(f"Using API URL: {search_api}")

    # 调用函数，传入需要的仓库和输出文件名
    get_dependents('AIDC-AI/ali-langengine', 'out/ali-langengine_test.json')
