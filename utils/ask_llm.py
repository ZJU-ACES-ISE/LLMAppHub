import requests
import json
import os
import yaml

class LLMAPI:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def call_api(self, prompt, model="qwen-max-latest"):
        headers = {
            'Accept': 'application/json',
            'Authorization': f"{self.api_key}",  # 这里放你的 DMXapi key
            'User-Agent': 'DMXAPI/1.0.0 (https://www.dmxapi.com)',  # 这里也改成 DMXAPI 的中转URL https://www.dmxapi.com，已经改好
            'Content-Type': 'application/json'
        }

        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(self.api_url, headers=headers, json=data)

        if response.status_code == 200:
            # response.json() 返回的是一个字典
            # response.text
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API call failed with status code {response.status_code}")


def read_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    llm_api = LLMAPI(config['llm_api_url'], config['api_key'])
    return llm_api # 返回一个 LLMAPI 实例

def get_url_from_llm(model_name):
    llm_api = read_config()

    # 构造提示信息
    prompt = f"""
    I am looking for the API URLs for different large language models. Please provide the API URL for the model I specify. For example, if I ask for the API URL of ChatGPT, you should respond with api.openai.com
    Here is the model:
    {model_name}
    Please provide only the correct API URLs, no extra explanations.
    """

    # 调用 API 并返回结果
    return llm_api.call_api(prompt)

def get_model_name_from_llm(api_url):
    llm_api = read_config()

    # 构造提示信息
    prompt = f"""
    I am looking for the names of different large language models. Please provide the name of the model that corresponds to the API URL I specify. For example, if I ask for the model name of api.openai.com, you should respond with ChatGPT.
    Here is the API URL:
    {api_url}
    Please provide only the correct model name,and the response with no blank space, no extra explanations.
    """
    return llm_api.call_api(prompt)

def get_repo_from_llm(model_name):
    llm_api = read_config()

    # 构造提示信息
    prompt = f"""
    You are an expert in retrieving GitHub repositories. Given the name of an AI model, your task is to provide the exact GitHub repository in the format: "owner/repository". Output only the repository path and nothing else.

    Example:
    Input: autogen
    Output: microsoft/autogen
    
    Now, process the following input:
    Input: {model_name}
    Output:
    """
    result = llm_api.call_api(prompt)
    print(f"框架的repo: {result}")
    # 调用 API 并返回结果
    return result

def get_dsl_keyword_from_llm():
    # 获取当前脚本的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(current_directory)
    # 返回到项目根目录
    project_root = os.path.dirname(current_directory)

    # 获取 dsl_example 文件夹的路径
    dsl_example_folder = os.path.join(project_root, 'dsl_example')

    # 列出 dsl_example 文件夹中的所有 YAML 文件
    files = [f for f in os.listdir(dsl_example_folder) if f.endswith('.yml') or f.endswith('.yaml')]

    # 检查是否找到 YAML 文件
    if files:
        # 假设选择第一个 YAML 文件
        config_file_path = os.path.join(dsl_example_folder, files[0])
        print(f"Using configuration file: {config_file_path}")

        # 读取并解析配置文件
        with open(config_file_path, 'r') as file:
            config_data = yaml.safe_load(file)

        llm_api = read_config()

        # 构造提示信息
        prompt = f"""
        You are an expert in analyzing YAML configuration files. I will provide you with a YAML configuration. Your task is to extract the important field from this configuration. These are the fields that represent key feature or decision-making parameters of the system.

        Please analyze the following YAML configuration and return only one field name that is important for understanding the system's configuration. Do not provide any additional explanation, only one field name.The feature keywords that use the dsl profile are extracted.

        Here is the YAML configuration:
        {yaml.dump(config_data, default_flow_style=False)}

        Output only the relevant field name (for example: 'suggested_questions_after_answer').
        """

        # 调用 API 并返回结果
        return llm_api.call_api(prompt)
    else:
        return "No YAML files found in the 'dsl_example' folder."





# 示例调用
if __name__ == "__main__":
    # 第一类
    # model_name = "gemini"
    # api_url = get_url_from_llm(model_name)
    # print(api_url)

    # 第二类
    # 直接调用函数并打印结果
    keyword = get_dsl_keyword_from_llm()
    print(keyword)