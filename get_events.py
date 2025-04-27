import requests
import time
import sys
import json
from datetime import datetime 
from openai import OpenAI
import re

API_ENDPOINT = "https://data-api.coindesk.com/v1/asset-events"
API_KEY = "de475fbec42eb9692e5b628b487a9196c613aa3962b5a57aa4288b6e1ef36a85"  # 替换为你的API密钥
def extract_json_blocks(text):
    """
    提取文本中以 ```json 开头并以 ``` 结尾的代码块内容。
    返回一个列表，每个元素是一个 JSON 块的字符串内容。
    """
    # 使用非贪婪模式提取 ```json ... ``` 之间的内容
    pattern = r"```json\s(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches][0]


def get_events(symbol, limit=100, to_ts=int(time.time()), lookup_priority="SYMBOL"):
    """
    获取指定资产的事件数据，返回API响应数据。
    
    :param symbol: 资产名称，例如"BTC"
    :param limit: 每次请求返回的最大事件数量，默认100
    :param to_ts: 截止时间戳，默认当前时间
    :param lookup_priority: 资产查询优先级，默认"SYMBOL"
    :return: API返回的JSON数据
    """
    print("📖 正在获取该代币的历史事件数据...")
    response = requests.get(
        'https://data-api.coindesk.com/asset/v1/events',
        params={
            "asset": symbol,
            "asset_lookup_priority": lookup_priority,
            "limit": limit,
            "to_ts": to_ts,
            "api_key": API_KEY
        },
        headers={"Content-type": "application/json; charset=UTF-8"}
    )
    json_response = response.json()

    # 简化数据，去除非必要字段，统一时间格式
    simplified_events = []
    for event in json_response.get("Data", []):
        simplified_event = {
            "id": event.get("ID"),
            "description": event.get("DESCRIPTION"),
            "announced_on": datetime.fromtimestamp(event.get("ANNOUNCED_ON")).strftime("%Y-%m-%d")
        }
        simplified_events.append(simplified_event)
    
    if not simplified_events:
        return None
    return json.dumps(simplified_events)

    # important_events = classify_asset_events(json.dumps(simplified_events))
    # # 将分类后的事件数据转换为JSON格式
    # important_events_json = json.loads(extract_json_blocks(important_events))

    # with open(f"history/{asset}_processed.json", "w", encoding="utf-8") as f:
    #     json.dump(important_events_json, f, indent=4, ensure_ascii=False)

    # return important_events_json


def classify_asset_events(events):
    """
    根据事件类型对事件进行分类，返回分类后的事件数据。
    
    :param events: 事件数据列表
    :return: 分类后的事件数据字典
    """
    print("🤔 正在分析事件数据...")
    client = OpenAI(
		api_key='sk-3ecff224d9a146e68780b3cd728dd7ae',
		base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
	)
    completion = client.chat.completions.create(
        model="qwen-plus", # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': 'You are a professional event classification expert.'},
            {'role': 'user', 'content': f'''Task:
Analyze a series of historical events related to a specific cryptocurrency and extract events that fall into the following categories:
	1.	Systemic regulatory policy changes
	2.	Macroeconomic or fiat currency liquidity shocks
	3.	Institutional-level fund flows

Requirements:
	•	Identify and extract all relevant events that match the categories above.
	•	Output the results in JSON format.
	•	Each event object should include a type field indicating the category it belongs to (e.g., "regulatory_change", "liquidity_shock", "institutional_flow").

The historical events data is as follows:
{events}
'''
            }
        ]
    )
    return completion.choices[0].message.content