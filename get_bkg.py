from openai import OpenAI
import json

def get_bkg(symbol):
	print("🤔 正在分析代币背景信息...")
	client = OpenAI(
		api_key='your-api-key-here',
		base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
	)
	reasoning_content = ""  # 定义完整思考过程
	answer_content = ""     # 定义完整回复
	is_answering = False   # 判断是否结束思考过程并开始回复

	# 创建聊天完成请求
	completion = client.chat.completions.create(
		model="qwq-plus",  # 此处以 qwq-plus 为例，可按需更换模型名称
		messages=[
			{'role': 'system', 'content': 'You are an expert in the field of cryptocurrency'},
			{"role": "user", "content": f"Analyze the background of token '{symbol}', including its history, technical design, team background."},
		],
		extra_body={
			"enable_search": True, # 开启联网搜索的参数
			"search_options": {
				"forced_search": True, # 强制联网搜索的参数
				"search_strategy": "pro" # 模型将搜索10条互联网信息
			}
		},
		# QwQ 模型仅支持流式输出方式调用
		stream=True,
		# 解除以下注释会在最后一个chunk返回Token使用量
		stream_options={
			"include_usage": True
		}
	)

	for chunk in completion:
		if not chunk.choices:
			pass
		else:
			delta = chunk.choices[0].delta
			# 打印思考过程
			if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
				reasoning_content += delta.reasoning_content
			else:
				# 开始回复
				if delta.content != "" and is_answering is False:
					is_answering = True
				answer_content += delta.content
	return json.dumps({f"Bachground of {symbol}": answer_content}, ensure_ascii=False, indent=4)


if __name__ == "__main__":
	symbol = "NEAR"
	result = get_bkg(symbol)
	print(result)