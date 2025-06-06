import subprocess
import time
import sys
from pathlib import Path

# --- 配置 ---
# 您要抓取的仓库
REPO_TO_SCRAPE = "openai/openai-python"
# 用于存放进度文件的目录
CSV_DIRECTORY = "github_dependents_info/output"
# 程序崩溃后，等待多少秒再重启
RESTART_DELAY = 10
# ---------------------


def run_scraper():
    """运行一次主程序，并返回其退出代码"""
    # 注意：这里的命令调用的是主模块，而不是run_persistent.py自身
    command = [
        sys.executable,  # 使用当前运行此脚本的Python解释器
        "-m",
        "github_dependents_info", # 调用主程序
        "--repo",
        REPO_TO_SCRAPE,
        "--csvdirectory",
        CSV_DIRECTORY,
        "--verbose",
    ]

    print(f"--- 开始抓取 {REPO_TO_SCRAPE} ---")
    print(f"运行命令: {' '.join(command)}")

    process = None
    try:
        # 使用 Popen 以便实时输出日志
        process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr)
        process.wait()  # 等待程序执行完毕
        return process.returncode
    except KeyboardInterrupt:
        print("\n--- “监工”脚本被中断，正在停止抓取程序... ---")
        if process:
            process.terminate()  # 尝试优雅地终止子进程
            try:
                process.wait(timeout=5)  # 等待5秒
            except subprocess.TimeoutExpired:
                process.kill()  # 如果无法终止，则强制结束
        # 以中断代码退出“监工”脚本
        sys.exit(130)
    except Exception as e:
        print(f"运行抓取脚本时发生未知错误: {e}")
        return -1  # 返回一个错误代码


def is_job_done(exit_code):
    """通过双重检查来判断任务是否真正完成"""
    # 检查条件1：程序是否正常退出
    is_clean_exit = exit_code == 0
    
    # 检查条件2：是否还有未完成的进度文件
    progress_files = list(Path(CSV_DIRECTORY).glob("*.next_url.txt"))
    has_pending_work = len(progress_files) > 0
    
    if has_pending_work:
        print(f"--- 检查到有 {len(progress_files)} 个任务仍在进行中... ---")

    # 只有在“正常退出”且“没有待办工作”时，任务才算完成
    return is_clean_exit and not has_pending_work


if __name__ == "__main__":
    # 将工作目录切换到脚本所在的目录，以确保相对路径正确
    # 这使得无论您从哪里运行此脚本，它都能找到主模块
    script_dir = Path(__file__).parent
    if script_dir.name == "github_dependents_info":
         # 如果脚本在包内，将工作目录设置为包的父目录
        import os
        os.chdir(script_dir.parent)


    while True:
        exit_code = run_scraper()

        if is_job_done(exit_code):
            print(f"\n--- 任务成功完成: {REPO_TO_SCRAPE} 的数据已全部抓取完毕。 ---")
            break  # 成功退出循环
        else:
            print(f"\n--- 监测到任务未完成或异常退出 (代码: {exit_code}) ---")
            print(f"--- {RESTART_DELAY} 秒后将自动重启... (按 Ctrl+C 可彻底终止) ---")
            try:
                time.sleep(RESTART_DELAY)
            except KeyboardInterrupt:
                print("\n--- “监工”脚本已被用户终止。 ---")
                break 