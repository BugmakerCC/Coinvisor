import requests 
import json
from datetime import datetime
from openai import OpenAI
import re

def extract_json_blocks(text):
    """
    提取文本中以 ```json 开头并以 ``` 结尾的代码块内容。
    返回一个列表，每个元素是一个 JSON 块的字符串内容。
    """
    # 使用非贪婪模式提取 ```json ... ``` 之间的内容
    pattern = r"```json\s(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches][0]

def get_news():
    """
    获取CoinDesk的新闻数据，返回API响应数据。
    
    :return: API返回的JSON数据
    """
    print("📝 正在获取当日最新的新闻数据...")
    result = []
    one_day_seconds = 24 * 60 * 60  # 一天的秒数
    # 请求CoinDesk新闻API
    response = requests.get('https://data-api.coindesk.com/news/v1/article/list',
        params={"lang":"EN","limit":100,"source_ids":"coindesk","api_key":"de475fbec42eb9692e5b628b487a9196c613aa3962b5a57aa4288b6e1ef36a85"},
        headers={"Content-type":"application/json; charset=UTF-8"}
    )

    json_response = response.json()
    for news in json_response.get("Data", []):
        if news.get("PUBLISHED_ON") < (int(datetime.now().timestamp()) - one_day_seconds):
            continue
        result.append({
            "Title": news.get("TITLE"),
            "Subtitle": news.get("SUBTITLE"),
            "Time": datetime.fromtimestamp(news.get("PUBLISHED_ON")).isoformat(),
            "Sentiment": news.get("SENTIMENT")
        })


    with open("news/news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    return json.dumps(result)


def analyze_news():
    """
    分析新闻数据，返回新闻摘要。

    :return: 新闻摘要字符串
    """
    news_data = get_news()
    print("🤔 正在总结新闻数据...")
    client = OpenAI(
		api_key='sk-3ecff224d9a146e68780b3cd728dd7ae',
		base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
	)
    completion = client.chat.completions.create(
        model="qwen-plus", # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': 'You are a cryptocurrency market analyst.'},
            {'role': 'user', 'content': f'''​**Task:​**​ 
Process today's news articles to:

1. ​**Score each article's market impact**​ (0-10 integer)
   - Criteria: Relevance to crypto, event scale, sentiment strength, timeliness, source credibility, secondary market links

2. ​**Create daily briefing**​ 
   - Highlight key themes, market implications, sentiment trends, and potential catalysts

​**Output Format:​**​
{{
  "analysis": [
    {{
      "Title": "...",
      "Subtitle": "...", 
      "Time": "...",
      "Sentiment": "...",
      "score": 0-10
    }},
    ...
  ],
  "summary": "..."
}}

​**Processing Rules:​**​
1. Maintain original news data intact
2. Prioritize regulatory/technical news

The news data is as follows:
{news_data}
'''
            }
        ]
    )
    return completion.choices[0].message.content

def news_sumary():
    summary = analyze_news()
    summary_json = json.loads(extract_json_blocks(summary))
    with open("news/news_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=4, ensure_ascii=False)
    return summary_json