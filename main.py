import argparse
import os.path

import c1_url
import c2_repo
from utils import ask_llm

def validate_repo_format(value):
    """
    验证仓库格式是否为owner/repo
    """
    if '/' not in value:
        raise argparse.ArgumentTypeError("必须使用 owner/repo 格式")
    parts = value.split('/')
    if len(parts) != 2 or not all(parts):
        raise argparse.ArgumentTypeError("无效的仓库格式，应为 owner/repo")
    return parts  # 返回分割后的列表 [owner, repo]


def main():
    global repo_owner
    parser = argparse.ArgumentParser(
        description="LLM 数据收集工具",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="启用详细输出"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="可用命令"
    )

    # API 收集子命令
    api_parser = subparsers.add_parser(
        "api",
        help="收集LLM API信息"
    )
    api_group = api_parser.add_mutually_exclusive_group(required=True)
    api_group.add_argument(
        "--url",
        type=str,
        help="直接指定LLM API的URL"
    )
    api_group.add_argument(
        "--framework",
        type=str,
        help="通过框架名称自动获取API URL"
    )
    api_parser.add_argument(
        "languages",
        nargs="+",
        metavar="LANGUAGE",
        help="指定要收集的编程语言（可多个，空格分隔）"
    )
    # api_parser.add_argument(
    #     "--output",
    #     type=str,
    #     default="apis.json",
    #     help="API信息输出路径"
    # )

    # Repo 收集子命令
    repo_parser = subparsers.add_parser(
        "repo",
        help="收集仓库信息"
    )
    repo_group = repo_parser.add_mutually_exclusive_group(required=True)
    repo_group.add_argument(
        "--framework",
        type=str,
        help="通过框架名称自动获取仓库信息"
    )
    # 修改repo命令解析部分
    repo_group.add_argument(
        "--manual",
        metavar="OWNER/REPO",
        type=validate_repo_format,  # 新增验证函数
        help="直接指定仓库信息 (格式: owner/repo)"
    )
    repo_parser.add_argument(
        "--output",
        type=str,
        default="repos.csv",
        help="仓库信息输出路径"
    )

    args = parser.parse_args()

    # 实际处理逻辑示例
    if args.command == "api":
        # target = args.url or args.framework
        source_type = "URL" if args.url else "NAME"
        # 添加核心处理逻辑
        if source_type == 'URL':
            # 当用户直接提供API URL时
            api_url = args.url
            model_name = ask_llm.get_model_name_from_llm(api_url)
        else:
            # 当用户提供框架名称时
            framework_name = args.framework
            api_url = ask_llm.get_url_from_llm(framework_name)
            model_name = ask_llm.get_model_name_from_llm(api_url)

        c1_url.collect_api_data(api_url, model_name, args.languages)


    # 修改repo命令处理逻辑

    elif args.command == "repo":
        if args.framework:
            # 这里添加框架处理逻辑
            repo_owner = ask_llm.get_repo_from_llm(args.framework)

        elif args.manual:
            owner, repo = args.manual  # 现在args.manual已经是分割后的列表
            repo_owner = f"{owner}/{repo}"
        c2_repo.get_dependents(repo_owner, os.path.join("out/api_repo/c2", repo_owner.replace("/","#") + ".json"))


if __name__ == "__main__":
    main()